import os
import shutil
import subprocess
import sys
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


def generate_stubs_for_package() -> None:
    """Generates typing stubs (`.pyi`) for the package using stubgen.<br>
    Certain files are copied as-is to preserve specific decorators and type hints."""

    print("\nGenerating stub files with stubgen...\n")

    try:
        skip_stubgen: set[Path] = {
            PROJECT_SRC / "base" / "consts.py",  # Preserve `@deprecated` decorators.
            PROJECT_SRC / "base" / "decorators.py",  # Preserve conditional typing imports.
            PROJECT_SRC / "format_codes.py",  # Preserve `@deprecated` decorators.
        }

        generated_count: int = 0
        skipped_count: int = 0

        for py_file in PROJECT_SRC.rglob("*.py"):
            pyi_file: Path = py_file.with_suffix(".pyi")
            rel_path: Path = py_file.relative_to(PROJECT_SRC.parent)

            if py_file in skip_stubgen:
                pyi_file.write_text(py_file.read_text(encoding="utf-8"), encoding="utf-8")
                print(f"  copied {rel_path.with_suffix('.pyi')} (preserving type definitions)")
                skipped_count += 1
                continue

            stubgen_exe: str = shutil.which("stubgen") or str(
                Path(sys.executable).parent / ("stubgen.exe" if sys.platform == "win32" else "stubgen")
            )
            result: subprocess.CompletedProcess[str] = subprocess.run(
                [stubgen_exe, str(py_file), "-o", "src", "--include-private", "--export-less"], capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"  generated {rel_path.with_suffix('.pyi')}")
                generated_count += 1
            else:
                print(f"  failed {rel_path}")
                if result.stderr:
                    print(f"    {result.stderr.strip()}")

        print(f"\nStub generation complete. ({generated_count} generated, {skipped_count} copied)\n")

    except Exception as exc:
        print(f"[WARNING] Could not generate stubs:\n  {'\n  '.join(str(exc).splitlines())}\n")


def clean_project_files(patterns: set[str], message: str) -> None:
    """Removes all files matching the given glob patterns from the source directory.<br>
    Prints a formatted success message if any files were deleted."""

    deleted_count = 0
    for pattern in patterns:
        for f in (PROJECT_ROOT / "src").rglob(pattern):
            try:
                f.unlink()
                deleted_count += 1
            except OSError:
                pass

    if deleted_count > 0:
        print(message.format(n=deleted_count, s="" if deleted_count == 1 else "s"))


if __name__ == "__main__":
    # If the user runs the setup script with the --gen-stubs flag,
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

            print("\nCompiling with mypyc...\n")
            source_files = find_python_files("src/xulbux")
            ext_modules = mypycify(source_files, opt_level="3")
            print("\nMypyc compilation complete.\n")

            generate_stubs_for_package()

        except (ImportError, Exception) as exc:
            print(
                "\n[WARNING] mypyc compilation disabled (not available or failed):\n"
                f"  {'\n  '.join(str(exc).splitlines())}\n"
                "\nInstalling as pure Python package...\n"
            )

    setup(name="xulbux", ext_modules=ext_modules)

    if _is_building:
        clean_project_files({"*.pyi"}, "\nCleaned up {n} stub file{s} from project directory.\n")

        if "--inplace" in sys.argv:
            clean_project_files(
                {"*.pyd", "*.so", "*.c"}, "\nCleaned up {n} compiled extension file{s} from project directory.\n"
            )
