import argparse
import importlib
import importlib.machinery
import importlib.util
import inspect
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# Ensure we can import xulbux:
ROOT_DIR = Path(__file__).parent.parent.resolve()
SRC_DIR = ROOT_DIR / "src"
DOCS_DIR = ROOT_DIR / "docs"
DOCS_SRC_DIR = DOCS_DIR / "src"
DOCS_BUILD_DIR = DOCS_DIR / ".build"

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


def generate_markdown_for_api(api_path: str) -> str:
    """Generates Markdown documentation for a given API path (e.g., `xulbux.console`)."""

    try:
        module = importlib.import_module(api_path)
        is_module = True

    except ModuleNotFoundError:
        # Might be a class or function inside a module:
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
            lines.append(module.__doc__.strip() + "\n")

        # List functions and classes:
        for name, obj in inspect.getmembers(module):
            if name.startswith("_"):
                continue
            elif (inspect.isfunction(obj) or inspect.isclass(obj)) and getattr(obj, "__module__", "") == api_path:
                lines.append(_generate_markdown_for_obj(name, obj))

        return "\n".join(lines)

    else:
        return f"> **Error**: Could not find API reference for `{api_path}`"


def format_signature_multiline(sig_text: str) -> str:
    """Forces the signature to span multiple lines with one argument per line."""

    # Add a trailing comma if it doesn't exist so Ruff formats it as multiline:
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

        # Put consecutive `/` and `*` on the same line:
        formatted = re.sub(r"\n\s*/,\n\s*\*,\n", "\n    /, *,\n", formatted)
        # Strip `self` and `cls` from the first argument:
        formatted = re.sub(r"\(\n    (?:self|cls)(?:\s*:[^,]*)?,\n\s*", "(\n    ", formatted)
        # If this leaves a stray `/` as the first argument, remove it:
        formatted = re.sub(r"\(\n    /,\n\s*", "(\n    ", formatted)

        # Remove private arguments:
        formatted = re.sub(r"\n\s+_[a-zA-Z0-9_]*[^,]*,", "", formatted)
        # Clean up stray markers if they are left at the end of the arguments list:
        formatted = re.sub(r"\n(\s*)/,\s*\*,\n\)", r"\n\1/,\n)", formatted)
        formatted = re.sub(r"\n\s*\*,\n\)", "\n)", formatted)

        # Clean up empty parentheses:
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


def _generate_markdown_for_obj(name: str, obj: Any) -> str:
    """Generates Markdown documentation for a given function or class object."""

    lines: list[str] = []

    if inspect.isfunction(obj):
        sig_str = get_source_signature(obj)
        lines.append('<div class="api-item">\n<div class="api-signature-col">\n')
        lines.append(f"```python\n{sig_str}\n```\n")
        lines.append('</div>\n<div class="api-docs-col">\n')
        lines.append(f"### `{name}`\n")
        if obj.__doc__:
            lines.append(obj.__doc__.strip() + "\n")
        lines.append("</div>\n</div>\n")

    elif inspect.isclass(obj):
        sig_str = get_class_signature(obj, name)
        lines.append('<div class="api-item">\n<div class="api-signature-col">\n')
        lines.append(f"```python\n{sig_str}\n```\n")
        lines.append('</div>\n<div class="api-docs-col">\n')
        lines.append(f"### `class {name}`\n")

        doc_parts: list[str] = []

        if obj.__doc__:
            doc_parts.append(obj.__doc__.strip())
        if (
            "__init__" in obj.__dict__
            and (init_obj := getattr(obj, "__init__", None))
            and init_obj is not object.__init__
            and init_obj.__doc__
            and init_obj.__doc__.strip() not in (obj.__doc__ or "")
        ):
            doc_parts.append(init_obj.__doc__.strip())

        if doc_parts:
            lines.append("\n\n".join(doc_parts) + "\n")

        lines.append("</div>\n</div>\n")

        # Methods:
        for m_name, m_obj in inspect.getmembers(obj):
            if m_name.startswith("_"):
                continue

            if inspect.isfunction(m_obj):
                m_sig_str = get_source_signature(m_obj)
                lines.append('<div class="api-item">\n<div class="api-signature-col">\n')
                lines.append(f"```python\n{m_sig_str}\n```\n")
                lines.append('</div>\n<div class="api-docs-col">\n')
                lines.append(f"#### `{m_name}`\n")
                if m_obj.__doc__:
                    lines.append(m_obj.__doc__.strip() + "\n")
                lines.append("</div>\n</div>\n")

    return "\n".join(lines)


def process_markdown_file(file_path: Path) -> None:
    """Processes a Markdown file, replacing API placeholders with generated documentation."""

    def replacer(match: re.Match[str]) -> str:
        api_path = match.group(1).strip()
        print(f"Generating docs for {api_path} in {file_path.name}...")
        return generate_markdown_for_api(api_path)

    pattern = re.compile(r"<!--\s*API:\s*([a-zA-Z0-9_.]+)\s*-->")
    new_content = pattern.sub(replacer, file_path.read_text(encoding="utf-8"))

    file_path.write_text(new_content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build xulbux documentation.")
    parser.add_argument("--dev", action="store_true", help="Run VitePress in dev mode")
    args = parser.parse_args()

    # [1] Clean and recreate build directory:
    if DOCS_BUILD_DIR.exists():
        shutil.rmtree(DOCS_BUILD_DIR)

    shutil.copytree(DOCS_SRC_DIR, DOCS_BUILD_DIR)
    print(f"Copied {DOCS_SRC_DIR.name} to {DOCS_BUILD_DIR.name}")

    # [2] Auto-discover modules and generate missing markdown files:
    sidebar_items: list[dict[str, str]] = []
    xulbux_dir = SRC_DIR / "xulbux"

    for py_file in sorted(xulbux_dir.rglob("*.py")):
        if py_file.name.startswith("__"):
            continue

        # Get relative path without extension to build module path:
        rel_path = py_file.relative_to(xulbux_dir).with_suffix("")
        api_path = f"xulbux.{str(rel_path).replace('/', '.')}"

        md_file_path = DOCS_BUILD_DIR / "docs" / f"{py_file.stem}.md"

        # If user manually created it in the root of `docs/src`, move it to `docs/`:
        manual_root_md = DOCS_BUILD_DIR / f"{py_file.stem}.md"
        if manual_root_md.exists():
            md_file_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(manual_root_md), str(md_file_path))

        # If manual MD doesn't exist, create it:
        if not md_file_path.exists():
            md_file_path.parent.mkdir(parents=True, exist_ok=True)
            title = py_file.stem.replace("_", " ").title()
            content = f"# {title} Module\n\n<!-- API: {api_path} -->\n"
            md_file_path.write_text(content, encoding="utf-8")
            print(f"Auto-generated {md_file_path.name} for {api_path}")

        sidebar_items.append({"text": py_file.stem.replace("_", " ").title(), "link": f"/docs/{py_file.stem}"})

    # Write `sidebar.json`:
    sidebar_data = [{"text": "API Reference", "items": sidebar_items}]
    sidebar_file = DOCS_BUILD_DIR / ".vitepress" / "sidebar.json"
    sidebar_file.parent.mkdir(parents=True, exist_ok=True)
    sidebar_file.write_text(json.dumps(sidebar_data, indent=2), encoding="utf-8")
    print(f"Generated sidebar.json with {len(sidebar_items)} items")

    # [3] Process all markdown files:
    for md_file in DOCS_BUILD_DIR.rglob("*.md"):
        if md_file.is_file():
            process_markdown_file(md_file)

    # [4] Run VitePress:
    cmd = ["pnpm", "exec", "vitepress", "dev" if args.dev else "build", ".build"]
    print(f"Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, cwd=DOCS_DIR, check=True)
    except subprocess.CalledProcessError as e:
        print(f"VitePress failed with exit code {e.returncode}")
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
