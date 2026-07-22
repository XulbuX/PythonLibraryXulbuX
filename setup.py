import ast
import os
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from setuptools import setup

PROJECT_ROOT = Path(__file__).parent
PROJECT_SRC = PROJECT_ROOT / "src" / "xulbux"


def find_python_files(directory: str) -> list[str]:
    """Recursively finds all Python source files in the
    specified directory, excluding `__init__.py` files."""

    python_files: list[str] = []

    for file in Path(directory).rglob("*.py"):
        if file.name == "__init__.py":
            continue
        python_files.append(str(file))

    return python_files


def clean_project_files(patterns: set[str], message: str) -> None:
    """Removes all files matching the given glob patterns from the source directory.<br>
    Prints a formatted success message if any files were deleted."""

    deleted_count = 0
    for pattern in patterns:
        for file in (PROJECT_ROOT / "src").rglob(pattern):
            try:
                file.unlink()
                deleted_count += 1
            except OSError:
                pass

    if deleted_count > 0:
        print(message.format(n=deleted_count, s="" if deleted_count == 1 else "s"), flush=True)


class StubGen(ast.NodeTransformer):
    """An AST transformer that generates `.pyi` stub files by stripping implementations."""

    def __init__(self, shadowed_names: set[str] | None = None) -> None:
        super().__init__()
        self.shadowed_names: set[str] = shadowed_names or set()

    @classmethod
    def generate_stubs(cls, py_files: Iterable[Path]) -> None:
        """Generate typing stubs (`.pyi`) for the provided Python files.<br>
        Certain files are copied as-is to preserve specific decorators and type hints."""

        print("\nGenerating stub files...\n", flush=True)

        generated_files: list[Path] = []
        generated_count: int = 0
        copied_count: int = 0

        for py_file in py_files:
            pyi_file: Path = py_file.with_suffix(".pyi")
            rel_path: Path = py_file.relative_to(PROJECT_SRC.parent)

            # Skip files with no content:
            if not py_file.read_text("utf-8").strip():
                pyi_file.write_text(py_file.read_text(encoding="utf-8"), encoding="utf-8")
                copied_count += 1
                print(f"  created {rel_path} (copied: empty file)", flush=True)
                continue

            try:
                out_file = cls._generate_stub_from(py_file, pyi_file.parent)
                generated_files.append(out_file.resolve())
                generated_count += 1
                print(f"  created {rel_path.with_suffix('.pyi')} (generated)", flush=True)

            except Exception as exc:
                pyi_file.write_text(py_file.read_text(encoding="utf-8"), encoding="utf-8")
                copied_count += 1
                print(f"  created {rel_path.with_suffix('.pyi')} (copied: {exc})", flush=True)

        if generated_files:
            # Format all generated stubs with Ruff in one call:
            subprocess.run(
                [sys.executable, "-m", "ruff", "check", *generated_files, "--fix", "--select", "I,F401,F841,UP"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ruff",
                    "format",
                    *generated_files,
                    "--line-length",
                    "9999",
                    "--config",
                    "format.skip-magic-trailing-comma=true",
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )

            # Add `noqa: E501`, but only to files that actually exceed the line-length
            # limit of 127 characters to prevent `Unused noqa directive` errors:
            for file in generated_files:
                content = file.read_text(encoding="utf-8")
                if any(len(line) > 127 for line in content.splitlines()):
                    file.write_text("# ruff: noqa: E501\n" + content, encoding="utf-8")

        print(f"\nStub generation complete. ({generated_count} generated, {copied_count} copied)\n\n", flush=True)

    @classmethod
    def _generate_stub_from(cls, source_file: Path, output_dir: Path) -> Path:
        """Generates a stub file in the specified output directory from the given source file."""

        # Transform the source file content into a stub using the AST transformer:
        src_code = source_file.read_text("utf-8")
        tree = ast.parse(src_code)

        shadowed_names = cls._get_type_checking_shadowed_names(tree)

        transformer = cls(shadowed_names=shadowed_names)
        transformed_tree = transformer.visit(tree)
        source = ast.unparse(transformed_tree)

        # Write the generated stub content to the output file:
        out_file = output_dir / source_file.with_suffix(".pyi").name
        out_file.write_text(source, encoding="utf-8")

        return out_file

    @staticmethod
    def _get_type_checking_shadowed_names(tree: ast.AST) -> set[str]:
        shadowed_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and (
                (isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING")
                or (
                    isinstance(node.test, ast.Attribute)
                    and isinstance(node.test.value, ast.Name)
                    and node.test.value.id == "typing"
                    and node.test.attr == "TYPE_CHECKING"
                )
            ):
                for subnode in ast.walk(node):
                    if isinstance(subnode, (ast.ImportFrom, ast.Import)):
                        for alias in subnode.names:
                            shadowed_names.add(alias.asname or alias.name)
        return shadowed_names

    def _is_overload_dec(self, dec: ast.expr) -> bool:
        if isinstance(dec, ast.Name) and dec.id == "overload":
            return True
        return bool(
            isinstance(dec, ast.Attribute)
            and isinstance(dec.value, ast.Name)
            and dec.value.id in ("typing", "typing_extensions")
            and dec.attr == "overload"
        )

    def _strip_unnecessary_impls(self, body: list[ast.stmt]) -> list[ast.stmt]:
        overloaded_names: set[str] = set()
        for stmt in body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(
                self._is_overload_dec(dec) for dec in stmt.decorator_list
            ):
                overloaded_names.add(stmt.name)

        new_body: list[ast.stmt] = []
        for stmt in body:
            if (
                isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))
                and stmt.name in overloaded_names
                and not any(self._is_overload_dec(dec) for dec in stmt.decorator_list)
            ):
                continue  # Drop the implementation function entirely.

            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                continue  # Drop variable docstrings.

            if isinstance(stmt, ast.Assign):
                targets = [ast.unparse(t) for t in stmt.targets]
                if not (len(targets) == 1 and targets[0] == "__all__"):
                    raise ValueError(
                        f"Constant(s) '{', '.join(targets)}' missing explicit type-hint. All variables must be strictly typed."
                    )

            new_body.append(stmt)

        return new_body

    def _strip_defaults(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for i in range(len(node.args.defaults)):
            node.args.defaults[i] = ast.Constant(value=Ellipsis)
        for i in range(len(node.args.kw_defaults)):
            if node.args.kw_defaults[i] is not None:
                node.args.kw_defaults[i] = ast.Constant(value=Ellipsis)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        self.generic_visit(node)
        if ast.get_docstring(node):
            node.body = node.body[1:]
        node.body = self._strip_unnecessary_impls(node.body)

        # Remove module-level `__getattr__` from stubs to prevent type checker issues:
        node.body = [
            stmt
            for stmt in node.body
            if not (isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)) and stmt.name == "__getattr__")
        ]

        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:  # noqa: C901
        existing_vars: set[str] = set()
        for stmt in node.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                existing_vars.add(stmt.target.id)
            elif isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        existing_vars.add(target.id)

        extracted_vars: list[ast.stmt] = []
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                for init_stmt in stmt.body:
                    if (
                        isinstance(init_stmt, ast.AnnAssign)
                        and isinstance(init_stmt.target, ast.Attribute)
                        and isinstance(init_stmt.target.value, ast.Name)
                        and init_stmt.target.value.id == "self"
                        and init_stmt.target.attr not in existing_vars
                    ):
                        var_name = init_stmt.target.attr
                        new_assign = ast.AnnAssign(
                            target=ast.Name(id=var_name, ctx=ast.Store()),
                            annotation=init_stmt.annotation,
                            value=None,
                            simple=1,
                        )
                        extracted_vars.append(new_assign)
                        existing_vars.add(var_name)

        self.generic_visit(node)
        if ast.get_docstring(node):
            node.body = node.body[1:]

        node.body = extracted_vars + self._strip_unnecessary_impls(node.body)

        dunder_vars: list[ast.stmt] = []
        other_stmts: list[ast.stmt] = []

        # Sort `node.body` to put dunder variables at the top:
        for stmt in node.body:
            is_dunder = False
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                if stmt.target.id.startswith("__") and stmt.target.id.endswith("__"):
                    is_dunder = True
            elif isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id.startswith("__") and target.id.endswith("__"):
                        is_dunder = True
                        break

            if is_dunder:
                dunder_vars.append(stmt)
            else:
                other_stmts.append(stmt)

        node.body = dunder_vars + other_stmts

        if not node.body:
            node.body = [ast.parse("...").body[0]]

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self.generic_visit(node)
        node.body = [ast.parse("...").body[0]]
        self._strip_defaults(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        self.generic_visit(node)
        node.body = [ast.parse("...").body[0]]
        self._strip_defaults(node)
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AnnAssign | None:
        if isinstance(node.target, ast.Name) and node.target.id in self.shadowed_names:
            return None
        self.generic_visit(node)
        node.value = None
        return node

    def visit_If(self, node: ast.If):
        self.generic_visit(node)
        if (isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING") or (
            isinstance(node.test, ast.Attribute)
            and isinstance(node.test.value, ast.Name)
            and node.test.value.id == "typing"
            and node.test.attr == "TYPE_CHECKING"
        ):
            return node.body
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self.generic_visit(node)
        if node.module in ("typing", "typing_extensions"):
            node.names = [n for n in node.names if n.name != "TYPE_CHECKING"]
            if not node.names:
                return None
        return node

    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        self.generic_visit(node)
        # Unwrap single-element tuples in subscript slices (removes trailing commas like in `Final[A,]`):
        if isinstance(node.slice, ast.Tuple) and len(node.slice.elts) == 1:
            node.slice = node.slice.elts[0]
        return node


def generate_stubs_for_package() -> None:
    """Generate typing stubs (`.pyi`) for the package."""
    try:
        StubGen.generate_stubs(PROJECT_SRC.rglob("*.py"))

    except Exception as exc:
        print(f"[WARNING] Could not generate stubs:\n  {'\n  '.join(str(exc).splitlines())}\n", flush=True)


if __name__ == "__main__":
    # If the user runs the setup script with the `--gen-stubs` flag,
    # generate stub files and exit without building the package:
    if "--gen-stubs" in sys.argv:
        generate_stubs_for_package()
        sys.exit(0)

    ext_modules = []

    # Only compile and generate stubs when actually building, not during metadata-only
    # phases (egg_info, dist_info) that pip invokes as part of PEP 517 preparation:
    _BUILD_COMMANDS = {"bdist_wheel", "build_ext", "build", "develop", "editable_wheel", "install"}
    _is_building = bool(set(sys.argv[1:]) & _BUILD_COMMANDS)

    # Optionally use MyPyC compilation:
    if os.environ.get("XULBUX_USE_MYPYC", "1") == "1" and _is_building:
        try:
            from mypyc.build import mypycify

            print("\nCompiling with mypyc...\n", flush=True)
            source_files = find_python_files("src/xulbux")
            ext_modules = mypycify(source_files, opt_level="3")
            print("\nMypyc compilation complete.\n", flush=True)

            generate_stubs_for_package()

        except (ImportError, Exception) as exc:
            print(
                "\n[WARNING] mypyc compilation disabled (not available or failed):\n"
                f"  {'\n  '.join(str(exc).splitlines())}\n"
                "\nInstalling as pure Python package...\n",
                flush=True,
            )

    setup(name="xulbux", ext_modules=ext_modules)

    if _is_building:
        clean_project_files({"*.pyi"}, "\nCleaned up {n} stub file{s} from project directory.\n")

        if "--inplace" in sys.argv:
            clean_project_files(
                {"*.pyd", "*.so", "*.c"}, "\nCleaned up {n} compiled extension file{s} from project directory.\n"
            )
