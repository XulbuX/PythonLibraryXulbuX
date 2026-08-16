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
XUL_DIR = SRC_DIR / "xulbux"
DOCS_DIR = ROOT_DIR / "docs"
DOCS_SRC_DIR = DOCS_DIR / "src"
DOCS_BUILD_DIR = DOCS_DIR / ".build"
SIDEBAR_REL_PATH = Path(".vitepress") / "sidebar.json"
API_OUT_DIR = DOCS_BUILD_DIR / "docs" / "api"

_DEPRECATED_ANNOTATED_RE = re.compile(r"(\[?)\s*Annotated\[\s*([\s\S]*?)\s*,\s*deprecated\([\s\S]*?\)\s*,?\s*\]\s*(\]?)")
"""Pattern to strip `Annotated[…, deprecated(…)]` wrappers if they exist."""

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


def _get_line_number(obj: Any) -> int:
    """Safely extracts the source-code line number of a given object."""

    try:
        return inspect.getsourcelines(obj)[1]
    except Exception:
        return getattr(getattr(obj, "__code__", None), "co_firstlineno", 0)


def extract_api_blocks(markdown: str) -> dict[str, str]:
    """Parses a markdown string and extracts tagged manual blocks."""

    blocks: dict[str, str] = {}
    pattern = re.compile(r"<!--\s*API:\s*<([a-zA-Z0-9_.]+)> \s*-->(.*?)<!--\s*API:\s*</\1>\s*-->", re.DOTALL)

    for match in pattern.finditer(markdown):
        blocks[match.group(1).strip()] = match.group(2).strip()

    return blocks


def _build_api_markdown_block(title: str, badge: str, signature: str, doc_parts: list[str]) -> str:
    """Builds a consistent HTML/Markdown block for an API item."""

    lines = [
        '<div class="api-item">\n\n',
        f"{title}{badge}\n\n",
        '<div class="api-signature-col">\n\n',
        f"```python\n{signature}\n```\n\n",
        '</div>\n\n<div class="api-docs-col">\n\n',
    ]

    if doc_parts:
        lines.append("\n\n".join(doc_parts) + "\n\n")
    lines.append("</div>\n\n</div>\n\n")

    return "".join(lines)


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

                    vars_info[var_name] = {
                        "sig": _DEPRECATED_ANNOTATED_RE.sub(r"\1\2\3", rep),
                        "doc": "",
                        "dep": "deprecated" in ast.unparse(stmt),
                        "line": getattr(stmt, "lineno", 0),
                    }

        elif type(stmt).__name__ == "TypeAlias":
            # Handle PEP 695 `type Name = ...` aliases:
            if not (var_name := str(getattr(name_node, "id", "")) if (name_node := getattr(stmt, "name", None)) else ""):
                continue
            last_target = var_name
            seg = ast.get_source_segment(source_code, stmt)
            rep = _dedent_source_segment(seg, stmt) if seg else ast.unparse(stmt)
            vars_info[var_name] = {
                "sig": _DEPRECATED_ANNOTATED_RE.sub(r"\1\2\3", rep),
                "doc": "",
                "dep": False,
                "line": getattr(stmt, "lineno", 0),
            }

        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            # Treat string literals immediately following a variable assignment as its docstring:
            if last_target and last_target in vars_info:
                vars_info[last_target]["doc"] = stmt.value.value
                last_target = None
        else:
            last_target = None

    return vars_info


def _generate_markdown_for_var(
    name: str,
    var_info: dict[str, Any],
    is_class_attr: bool = False,
    class_name: str = "",
    blocks: dict[str, str] | None = None,
) -> str:
    """Generates Markdown documentation for a given variable or class attribute."""

    if blocks is None:
        blocks = {}

    badge = ' <Badge type="danger" text="deprecated" />' if var_info["dep"] else ""
    if is_class_attr and class_name:
        title = (
            f'#### <code><a class="class-prefix" href="#{class_name.lower()}"'
            f' data-class-prefix="{class_name}"></a>.{name}</code>'
        )
    elif is_class_attr:
        title = f"#### `.{name}`"
    else:
        title = f"### `{name}`"

    doc_parts = [process_docstring(var_info["doc"])] if var_info["doc"] else []

    block_key = f"{class_name}.{name}" if class_name else name
    if block_key in blocks:
        doc_parts.append(blocks[block_key])

    return _build_api_markdown_block(title, badge, var_info["sig"], doc_parts)


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


def generate_md_for_api(api_path: str, blocks: dict[str, str] | None = None) -> str:  # ruff:ignore[complex-structure]
    """Generates Markdown documentation for a given API path (e.g., `xulbux.console`)."""

    if blocks is None:
        blocks = {}

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
                return _generate_markdown_for_obj(parts[1], getattr(module, parts[1]), blocks=blocks)

            except (ModuleNotFoundError, AttributeError):
                return f"> **Error**: Could not find API reference for `{api_path}`"

        return f"> **Error**: Could not find module `{api_path}`"

    if is_module:
        lines: list[str] = []
        lines.append(f"# {api_path.split('.')[-1].replace('_', ' ').title()} Module\n")

        if module.__doc__:
            lines.append(process_docstring(module.__doc__) + "\n")

        if "_header" in blocks:
            lines.append(blocks["_header"] + "\n")

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

        items_to_document: list[tuple[int, str, Any, Any]] = []

        for name, var_info in module_vars.items():
            if not name.startswith("_"):
                # Skip variable aliases for module-defined classes/functions, as they get fully documented below:
                if (
                    (obj := getattr(module, name, None))
                    and (inspect.isfunction(obj) or inspect.isclass(obj))
                    and getattr(obj, "__module__", "") == api_path
                ):
                    continue
                items_to_document.append((var_info.get("line", 0), "var", name, var_info))

        # List functions and classes:
        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue
            elif (inspect.isfunction(obj) or inspect.isclass(obj)) and getattr(obj, "__module__", "") == api_path:
                items_to_document.append((_get_line_number(obj), "obj", name, obj))

        # Sort items by their source-code line number to ensure a logical reading flow:
        items_to_document.sort(key=lambda x: x[0])

        for item in items_to_document:
            if item[1] == "var":
                lines.append(_generate_markdown_for_var(item[2], item[3], blocks=blocks))
            else:
                lines.append(_generate_markdown_for_obj(item[2], item[3], classes_ast.get(item[2], {}), blocks=blocks))

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


def _generate_markdown_for_obj(  # ruff:ignore[complex-structure]
    name: str,
    obj: Any,
    class_vars: dict[str, dict[str, Any]] | None = None,
    blocks: dict[str, str] | None = None,
    class_name: str = "",
) -> str:
    """Generates Markdown documentation for a given function, class, or method object."""

    if class_vars is None:
        class_vars = {}
    if blocks is None:
        blocks = {}

    badge: str = ' <Badge type="danger" text="deprecated" />' if hasattr(obj, "__deprecated__") else ""
    doc_parts: list[str] = []
    lines: list[str] = []

    if inspect.isfunction(obj) or inspect.ismethod(obj):
        if class_name:
            title = (
                f'#### <code><a class="class-prefix" href="#{class_name.lower()}"'
                f' data-class-prefix="{class_name}"></a>.{name}()</code>'
            )
            block_key = f"{class_name}.{name}"
        else:
            title = f"### `{name}()`"
            block_key = name

        if obj.__doc__:
            doc_parts.append(process_docstring(obj.__doc__))
        if block_key in blocks:
            doc_parts.append(blocks[block_key])

        lines.append(_build_api_markdown_block(title, badge, get_source_signature(obj), doc_parts))

    elif inspect.isclass(obj):
        title = f"### `{name}`"

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

        if name in blocks:
            doc_parts.append(blocks[name])

        lines.append(_build_api_markdown_block(title, badge, get_class_signature(obj, name), doc_parts))

        items_to_doc: list[tuple[int, str, Any, Any]] = []

        # Class variables:
        for v_name, v_info in class_vars.items():
            if not v_name.startswith("_"):
                items_to_doc.append((v_info.get("line", 0), "var", v_name, v_info))

        # Methods:
        for m_name, m_obj in inspect.getmembers(obj):
            if m_name.startswith("_"):
                continue

            if inspect.isfunction(m_obj) or inspect.ismethod(m_obj):
                items_to_doc.append((_get_line_number(m_obj), "meth", m_name, m_obj))

        # Sort items by their source-code line number to ensure a logical reading flow:
        items_to_doc.sort(key=lambda x: x[0])

        for item in items_to_doc:
            if item[1] == "var":
                lines.append(_generate_markdown_for_var(item[2], item[3], is_class_attr=True, class_name=name, blocks=blocks))
            else:
                lines.append(_generate_markdown_for_obj(item[2], item[3], blocks=blocks, class_name=name))

    return "\n".join(lines)


def process_markdown_file(src_path: Path, dest_path: Path | None = None, api_path: str | None = None) -> None:
    """Processes a manual API Markdown file, injecting its blocks into the auto-generated API structure."""

    if api_path is None:
        try:
            if "api" in src_path.parts:
                api_idx = src_path.parts.index("api")
                rel_parts = src_path.parts[api_idx + 1 :]
                api_path = f"xulbux.{'.'.join(rel_parts)[:-3]}" if src_path.suffix == ".md" else None
        except ValueError:
            pass

    if not api_path:
        # Not an API file; just copy it if a different destination was requested:
        if dest_path and dest_path != src_path:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
        return

    blocks = extract_api_blocks(src_path.read_text(encoding="utf-8")) if src_path.exists() else {}
    final_md = generate_md_for_api(api_path, blocks)

    out_path = dest_path or src_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(final_md, encoding="utf-8")

    print(f"  generated {out_path.name} ({api_path})")


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
    parser.add_argument("--process-file", nargs=2, metavar=("SRC", "DEST"), help="Process a single MD file from SRC to DEST")
    args = parser.parse_args()

    if args.process_file:
        process_markdown_file(Path(args.process_file[0]), Path(args.process_file[1]))
        return

    # [1] Clean and recreate the build directory to ensure a fresh slate:
    if DOCS_BUILD_DIR.exists():
        shutil.rmtree(DOCS_BUILD_DIR)

    shutil.copytree(DOCS_SRC_DIR, DOCS_BUILD_DIR)
    print(f"\nCopied {DOCS_SRC_DIR.name} to {DOCS_BUILD_DIR.name}\n")

    # [2] Auto-discover all Python modules and generate markdown files for them:
    sidebar_root_items: list[dict[str, Any]] = []
    sidebar_groups: dict[str, list[dict[str, str]]] = {}
    sidebar_items: list[dict[str, Any]] = []

    for py_file in sorted(XUL_DIR.rglob("*.py")):
        if py_file.name.startswith("_"):
            continue

        rel_path = py_file.relative_to(XUL_DIR).with_suffix("")
        flat_module_path = str(rel_path).replace("\\", "/").replace("/", ".")

        api_path = f"xulbux.{flat_module_path}"
        page_title = py_file.stem.replace("_", " ").title()

        md_file_path = API_OUT_DIR / f"{flat_module_path}.md"
        link_path = f"/docs/api/{flat_module_path}"

        process_markdown_file(md_file_path, api_path=api_path)

        item = {"text": page_title, "link": link_path}

        if len(rel_path.parts) > 1:
            group_name = rel_path.parts[0].title()
            if group_name not in sidebar_groups:
                sidebar_groups[group_name] = []
            sidebar_groups[group_name].append(item)
        else:
            sidebar_root_items.append(item)

    for group_name, items in sorted(sidebar_groups.items()):
        sidebar_items.append({"text": group_name, "collapsed": False, "items": items})
    sidebar_items.extend(sidebar_root_items)

    # Write `sidebar.json`:
    sidebar_data = get_base_sidebar(DOCS_SRC_DIR)
    sidebar_data.append({"text": "API Reference", "items": sidebar_items})

    sidebar_file = DOCS_BUILD_DIR / SIDEBAR_REL_PATH
    sidebar_file.parent.mkdir(parents=True, exist_ok=True)
    sidebar_file.write_text(json.dumps(sidebar_data, indent=2), encoding="utf-8")
    print(f"\nGenerated sidebar.json with {len(sidebar_root_items) + sum(len(i) for i in sidebar_groups.values())} items\n")

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
