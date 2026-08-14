import argparse
import ast
import importlib
import importlib.machinery
import importlib.util
import inspect
import json
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

# Ensure we can import xulbux:
ROOT_DIR = Path(__file__).parent.parent.resolve()
SRC_DIR = ROOT_DIR / "src"
DOCS_DIR = ROOT_DIR / "docs"
DOCS_SRC_DIR = DOCS_DIR / "src"
DOCS_BUILD_DIR = DOCS_DIR / ".build"
SIDEBAR_REL_PATH = Path(".vitepress") / "sidebar.json"

sys.path.insert(0, str(SRC_DIR))


class PyOnlyFinder:
    """A custom module finder that only allows importing Python files from the `src` directory."""

    @classmethod
    def find_spec(cls, fullname: str, path: Any, target: Any = None) -> Any:
        """Finds the module spec for a given module name, but only if it starts with `xulbux`."""

        if not fullname.startswith("xulbux"):
            return None

        parts = fullname.split(".")
        py_path = SRC_DIR.joinpath(*parts).with_suffix(".py")

        if not py_path.exists():
            py_path = SRC_DIR.joinpath(*parts, "__init__.py")
            if not py_path.exists():
                return None

        return importlib.util.spec_from_file_location(
            fullname, str(py_path), loader=importlib.machinery.SourceFileLoader(fullname, str(py_path))
        )


sys.meta_path.insert(0, PyOnlyFinder)


def _dedent_source_segment(segment: str, stmt: ast.stmt) -> str:
    """Restores the first line's indentation and de-dents the entire block."""

    if not segment:
        return segment

    return textwrap.dedent((" " * getattr(stmt, "col_offset", 0)) + segment).strip()


def _extract_ast_vars(body: list[ast.stmt], source_code: str) -> dict[str, dict[str, Any]]:
    """Extracts variables, type aliases, and their docstrings from an AST body."""

    last_target: str | None = None
    vars_info: dict[str, dict[str, Any]] = {}

    for stmt in body:
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            for target in stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]:
                if isinstance(target, ast.Name):
                    last_target = (var_name := target.id)
                    seg = ast.get_source_segment(source_code, stmt)
                    # Use original formatting via `seg` if available, otherwise fallback to `ast.unparse()`:
                    rep = _dedent_source_segment(seg, stmt) if seg else ast.unparse(stmt)

                    # Truncate large multiline calls (e.g. `StyledText(...)`) by replacing arguments with `...`:
                    if rep.count("\n") > 3 and isinstance(stmt.value, ast.Call):
                        stmt.value.args = [ast.Constant(value=Ellipsis)]
                        stmt.value.keywords = []
                        rep = ast.unparse(stmt)

                    # Strip `Annotated[..., deprecated(...)]` wrappers, greedily collapsing outer brackets if they exist:
                    rep = re.sub(
                        r"(\[?)\s*Annotated\[\s*([\s\S]*?)\s*,\s*deprecated\([\s\S]*?\)\s*,?\s*\]\s*(\]?)", r"\1\2\3", rep
                    )
                    vars_info[var_name] = {"sig": rep, "doc": "", "dep": "deprecated" in ast.unparse(stmt)}

        elif type(stmt).__name__ == "TypeAlias":
            # Handle PEP 695 `type Name = ...` aliases:
            if not (var_name := str(getattr(name_node, "id", "")) if (name_node := getattr(stmt, "name", None)) else ""):
                continue
            last_target = var_name
            seg = ast.get_source_segment(source_code, stmt)
            rep = _dedent_source_segment(seg, stmt) if seg else ast.unparse(stmt)
            # Strip `Annotated` wrappers from type aliases just like we do for variable assignments:
            rep = re.sub(r"(\[?)\s*Annotated\[\s*([\s\S]*?)\s*,\s*deprecated\([\s\S]*?\)\s*,?\s*\]\s*(\]?)", r"\1\2\3", rep)
            vars_info[var_name] = {"sig": rep, "doc": "", "dep": False}

        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            # Treat string literals immediately following a variable assignment as its docstring:
            if last_target and last_target in vars_info:
                vars_info[last_target]["doc"] = stmt.value.value
                last_target = None
        else:
            last_target = None

    return vars_info


def _generate_markdown_for_var(name: str, var_info: dict[str, Any], is_class_attr: bool = False) -> str:
    """Generates Markdown documentation for a given variable or class attribute."""

    badge = ' <Badge type="danger" text="deprecated" />' if var_info["dep"] else ""
    lines: list[str] = []
    lines.append('<div class="api-item">\n')
    lines.append(f"{'####' if is_class_attr else '###'} `.{name}`{badge}\n" if is_class_attr else f"### `{name}`{badge}\n")
    lines.append('<div class="api-signature-col">\n')
    lines.append(f"```python\n{var_info['sig']}\n```\n")
    lines.append('</div>\n<div class="api-docs-col">\n')
    if var_info["doc"]:
        lines.append(process_docstring(var_info["doc"]) + "\n")
    lines.append("</div>\n</div>\n")

    return "\n".join(lines)


def process_docstring(doc: str | None) -> str:
    """Cleans up docstring indentation and converts `>>> ` doc-tests into Python code blocks."""

    if not doc:
        return ""

    lines = (doc := inspect.cleandoc(doc)).split("\n")
    out: list[str] = []
    in_code = False

    for line in lines:
        if (stripped := line.lstrip()).startswith(">>> ") or stripped.startswith("... "):
            if not in_code:
                out.append("```python")
                in_code = True
            out.append(stripped)
        else:
            if in_code:
                out.append("```")
                in_code = False
            out.append(line)

    if in_code:
        out.append("```")

    return "\n".join(out)


def generate_md_for_api(api_path: str) -> str:  # noqa: C901
    """Generates Markdown documentation for a given API path (e.g., `xulbux.console`)."""

    try:
        # Attempt to import the API path as a full module:
        module = importlib.import_module(api_path)
        is_module = True

    except ModuleNotFoundError:
        # Fallback: check if the path points to a specific class or function inside a module:
        if len(parts := api_path.rsplit(".", 1)) == 2:
            try:
                module = importlib.import_module(parts[0])
                is_module = False
                return _generate_markdown_for_obj(parts[1], getattr(module, parts[1]))

            except (ModuleNotFoundError, AttributeError):
                return f"> **Error**: Could not find API reference for `{api_path}`"

        return f"> **Error**: Could not find module `{api_path}`"

    if is_module:
        lines: list[str] = []

        if module.__doc__:
            lines.append(process_docstring(module.__doc__) + "\n")

        tree = None
        source_code = ""
        # Parse the AST to extract exact variable definitions and docstrings (which `inspect` cannot see):
        try:
            if source_file := inspect.getsourcefile(module):
                source_code = Path(source_file).read_text("utf-8")
                tree = ast.parse(source_code)
        except Exception:
            pass

        # Extract module-level variables:
        module_vars = _extract_ast_vars(tree.body, source_code) if tree else {}
        classes_ast: dict[str, dict[str, dict[str, Any]]] = {}

        # Extract class-level variables (attributes):
        if tree:
            for stmt in tree.body:
                if isinstance(stmt, ast.ClassDef):
                    classes_ast[stmt.name] = _extract_ast_vars(stmt.body, source_code)

        for name, var_info in module_vars.items():
            if not name.startswith("_"):
                # Skip variable aliases for module-defined classes/functions, as they get fully documented below:
                if (
                    (obj := getattr(module, name, None))
                    and (inspect.isfunction(obj) or inspect.isclass(obj))
                    and getattr(obj, "__module__", "") == api_path
                ):
                    continue
                lines.append(_generate_markdown_for_var(name, var_info))

        # List functions and classes:
        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue
            elif (inspect.isfunction(obj) or inspect.isclass(obj)) and getattr(obj, "__module__", "") == api_path:
                lines.append(_generate_markdown_for_obj(name, obj, classes_ast.get(name, {})))

        return "\n".join(lines)

    else:
        return f"> **Error**: Could not find API reference for `{api_path}`"


def format_signature_multiline(sig_text: str) -> str:
    """Forces the signature to span multiple lines with one argument per line."""

    # Add a trailing comma if missing to force Ruff to format the signature across multiple lines:
    sig = re.sub(r",?\s*\)\s*(->\s*[^:]+)?\s*:?$", r",) \1:", sig_text)
    # Append a dummy body so the code is syntactically valid for Ruff:
    sig += "\n    pass\n"

    try:
        res = subprocess.run(
            [sys.executable, "-m", "ruff", "format", "-", "--config", "format.skip-magic-trailing-comma=false"],
            input=sig,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )

        if (formatted := res.stdout.strip()).endswith("\n    pass"):
            formatted = formatted[:-9]
        if formatted.endswith(":"):
            formatted = formatted[:-1]

        # Put consecutive `/` and `*` (positional/keyword-only markers) onto the same line:
        formatted = re.sub(r"\n\s*/,\n\s*\*,\n", "\n    /, *,\n", formatted)
        # Strip `self` and `cls` parameters since they don't need to be in the public docs:
        formatted = re.sub(r"\(\n    (?:self|cls)(?:\s*:[^,]*)?,\n\s*", "(\n    ", formatted)
        # If this leaves a stray `/` as the first argument, remove it:
        formatted = re.sub(r"\(\n    /,\n\s*", "(\n    ", formatted)

        # Remove internal private arguments (starting with `_`).
        formatted = re.sub(r"\n\s+_[a-zA-Z0-9_]*[^\n]*", "", formatted)
        # Clean up stray markers if they are left dangling at the end of the arguments list:
        formatted = re.sub(r"\n(\s*)/,\s*\*,\n\)", r"\n\1/,\n)", formatted)
        formatted = re.sub(r"\n\s*\*,\n\)", "\n)", formatted)

        # Clean up any empty parentheses caused by stripping arguments:
        formatted = formatted.replace("(\n    )", "()")

        return formatted

    except Exception:
        if sig_text.endswith(":"):
            return sig_text[:-1]

        return sig_text


def get_source_signature(obj: Any) -> str:
    """Returns the source signature of a function or class, including decorators and docstring if available."""

    try:
        lines, _ = inspect.getsourcelines(obj)
    except Exception:
        try:
            return str(inspect.signature(obj))
        except Exception:
            return "(...)"

    sig_lines: list[str] = []
    in_sig: bool = False

    for line in lines:
        if not in_sig:
            if (stripped := line.strip()).startswith("def ") or stripped.startswith("class "):
                sig_lines.append(line)
                in_sig = True
        else:
            sig_lines.append(line)

        if (
            in_sig
            and (combined := "".join(sig_lines)).count("(") == combined.count(")")
            and ":" in combined[combined.rfind(")") + 1 :]
        ):
            break

    if (sig_text := "".join(sig_lines).strip()).endswith(":"):
        sig_text = sig_text[:-1].strip()

    return format_signature_multiline(sig_text)


def get_class_signature(cls_obj: Any, cls_name: str) -> str:
    """Returns the class signature by parsing its __init__ method, matching VS Code's style."""
    try:
        if (
            (init_obj := cls_obj.__dict__.get("__init__")) is None
            or getattr(init_obj, "__name__", "") != "__init__"
            or init_obj is object.__init__
        ):
            return f"class {cls_name}"

        init_sig = get_source_signature(init_obj)

        sig = re.sub(r"^def\s+__init__", f"class {cls_name}", init_sig)
        sig = re.sub(r"\(\s*\n\s*\n", "(\n", sig)
        sig = re.sub(r"\)\s*(?:->\s*.*)?$", ")", sig)

        return sig.replace("()", "")

    except Exception:
        return f"class {cls_name}"


def _generate_markdown_for_obj(name: str, obj: Any, class_vars: dict[str, dict[str, Any]] | None = None) -> str:  # noqa: C901
    """Generates Markdown documentation for a given function or class object."""

    if class_vars is None:
        class_vars = {}

    badge: str = ' <Badge type="danger" text="deprecated" />' if hasattr(obj, "__deprecated__") else ""
    lines: list[str] = []

    if inspect.isfunction(obj):
        sig_str = get_source_signature(obj)
        lines.append('<div class="api-item">\n')
        lines.append(f"### `{name}()`{badge}\n")
        lines.append('<div class="api-signature-col">\n')
        lines.append(f"```python\n{sig_str}\n```\n")
        lines.append('</div>\n<div class="api-docs-col">\n')
        if obj.__doc__:
            lines.append(process_docstring(obj.__doc__) + "\n")
        lines.append("</div>\n</div>\n")

    elif inspect.isclass(obj):
        sig_str = get_class_signature(obj, name)
        lines.append('<div class="api-item">\n')
        lines.append(f"### `{name}`{badge}\n")
        lines.append('<div class="api-signature-col">\n')
        lines.append(f"```python\n{sig_str}\n```\n")
        lines.append('</div>\n<div class="api-docs-col">\n')

        doc_parts: list[str] = []

        if obj.__doc__:
            doc_parts.append(process_docstring(obj.__doc__))
        if (
            "__init__" in obj.__dict__
            and (init_obj := getattr(obj, "__init__", None))
            and init_obj is not object.__init__
            and init_obj.__doc__
            and process_docstring(init_obj.__doc__) not in process_docstring(obj.__doc__)
        ):
            doc_parts.append(process_docstring(init_obj.__doc__))

        if doc_parts:
            lines.append("\n\n".join(doc_parts) + "\n")

        lines.append("</div>\n</div>\n")

        # Class variables:
        for v_name, v_info in class_vars.items():
            if not v_name.startswith("_"):
                lines.append(_generate_markdown_for_var(v_name, v_info, is_class_attr=True))

        # Methods:
        for m_name, m_obj in inspect.getmembers(obj):
            if m_name.startswith("_"):
                continue

            if inspect.isfunction(m_obj) or inspect.ismethod(m_obj):
                m_sig_str = get_source_signature(m_obj)
                badge = ' <Badge type="danger" text="deprecated" />' if hasattr(m_obj, "__deprecated__") else ""
                lines.append('<div class="api-item">\n')
                lines.append(f"#### `.{m_name}()`{badge}\n")
                lines.append('<div class="api-signature-col">\n')
                lines.append(f"```python\n{m_sig_str}\n```\n")
                lines.append('</div>\n<div class="api-docs-col">\n')
                if m_obj.__doc__:
                    lines.append(process_docstring(m_obj.__doc__) + "\n")
                lines.append("</div>\n</div>\n")

    return "\n".join(lines)


def process_markdown_file(file_path: Path) -> None:
    """Processes a Markdown file, replacing API placeholders with generated documentation."""

    api_path: str = ""

    def replacer(match: re.Match[str]) -> str:
        nonlocal api_path
        api_path = match.group(1).strip()
        return generate_md_for_api(api_path)

    file_path.write_text(
        re.compile(r"<!--\s*API:\s*([a-zA-Z0-9_.]+)\s*-->").sub(replacer, file_path.read_text(encoding="utf-8")),
        encoding="utf-8",
    )

    print(f"  generated {file_path.name}{f' ({api_path})' if api_path else ''}")


def get_base_sidebar(docs_src_dir: Path) -> list[Any]:
    """Returns the base sidebar structure from the `.vitepress/sidebar.json` file in<br>
    the `docs/src` directory, or an empty list if the file doesn't exist or is invalid."""

    src_sidebar_file = docs_src_dir / SIDEBAR_REL_PATH

    if src_sidebar_file.exists() and (src_content := src_sidebar_file.read_text(encoding="utf-8").strip()):
        try:
            parsed = json.loads(src_content)
            if isinstance(parsed, list):
                return parsed  # type: ignore
        except json.JSONDecodeError:
            pass

    return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Build xulbux documentation.")
    parser.add_argument("--dev", action="store_true", help="Run VitePress in dev mode")
    args = parser.parse_args()

    # [1] Clean and recreate the build directory to ensure a fresh slate:
    if DOCS_BUILD_DIR.exists():
        shutil.rmtree(DOCS_BUILD_DIR)

    shutil.copytree(DOCS_SRC_DIR, DOCS_BUILD_DIR)
    print(f"\nCopied {DOCS_SRC_DIR.name} to {DOCS_BUILD_DIR.name}\n")

    # [2] Auto-discover all Python modules and generate placeholder markdown files for them:
    sidebar_items: list[dict[str, str]] = []
    xulbux_dir = SRC_DIR / "xulbux"

    for py_file in sorted(xulbux_dir.rglob("*.py")):
        if py_file.name.startswith("__"):
            continue

        # Get relative path without extension to build module path:
        rel_path = py_file.relative_to(xulbux_dir).with_suffix("")
        api_path = f"xulbux.{str(rel_path).replace('\\', '/').replace('/', '.')}"

        page_slug = py_file.stem.replace("_", "-")
        page_title = py_file.stem.replace("_", " ").title()
        md_file_path = DOCS_BUILD_DIR / "docs" / f"{page_slug}.md"

        # If user manually created it in the root of `docs/src`, move it to `docs/`:
        if (manual_root_md := DOCS_BUILD_DIR / f"{page_slug}.md").exists():
            md_file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(manual_root_md), str(md_file_path))

        # If manual MD doesn't exist, create it:
        if not md_file_path.exists():
            md_file_path.parent.mkdir(parents=True, exist_ok=True)
            md_file_path.write_text(f"# {page_title} Module\n\n<!-- API: {api_path} -->\n", encoding="utf-8")
            print(f"  created {md_file_path.name} ({api_path})")

        sidebar_items.append({"text": page_title, "link": f"/docs/{page_slug}"})

    # Write `sidebar.json`:
    sidebar_data = get_base_sidebar(DOCS_SRC_DIR)
    sidebar_data.append({"text": "API Reference", "items": sidebar_items})

    sidebar_file = DOCS_BUILD_DIR / SIDEBAR_REL_PATH
    sidebar_file.parent.mkdir(parents=True, exist_ok=True)
    sidebar_file.write_text(json.dumps(sidebar_data, indent=2), encoding="utf-8")
    print(f"\nGenerated sidebar.json with {len(sidebar_items)} items\n")

    # [3] Process all markdown files, injecting the actual API docs wherever `<!-- API: ... -->` is found:
    for md_file in DOCS_BUILD_DIR.rglob("*.md"):
        if md_file.is_file():
            process_markdown_file(md_file)

    # [4] Build or serve the final site using VitePress:
    if not (pnpm_exe := shutil.which("pnpm")):
        print("[ERROR] pnpm is not installed or not in PATH.")
        sys.exit(1)

    print(f"\nRunning VitePress {'dev' if args.dev else 'build'}...\n")

    try:
        subprocess.run([pnpm_exe, "exec", "vitepress", "dev" if args.dev else "build", ".build"], cwd=DOCS_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"VitePress failed with exit code {e.returncode}\n")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
