from setuptools import setup
from pathlib import Path
import subprocess
import shutil
import sys
import os


PROJECT_ROOT = Path(__file__).parent
PROJECT_SRC = PROJECT_ROOT / "src" / "xulbux"


def find_python_files(directory: str) -> list[str]:
    python_files: list[str] = []
    for file in Path(directory).rglob("*.py"):
        if file.name == "__init__.py":
            continue
        python_files.append(str(file))
    return python_files


def generate_stubs_for_package():
    print("\nGenerating stub files with stubgen...\n")

    try:
        skip_stubgen = {
            PROJECT_SRC / "base" / "types.py",  # Complex type definitions
            PROJECT_SRC / "__init__.py",  # Preserve package metadata constants.
        }

        generated_count = 0
        skipped_count = 0

        for py_file in PROJECT_SRC.rglob("*.py"):
            pyi_file = py_file.with_suffix(".pyi")
            rel_path = py_file.relative_to(PROJECT_SRC.parent)

            if py_file in skip_stubgen:
                pyi_file.write_text(py_file.read_text(encoding="utf-8"), encoding="utf-8")
                print(f"  copied {rel_path.with_suffix('.pyi')} (preserving type definitions)")
                skipped_count += 1
                continue

            stubgen_exe = (
                shutil.which("stubgen")
                or str(Path(sys.executable).parent / ("stubgen.exe" if sys.platform == "win32" else "stubgen"))
            )
            result = subprocess.run(
                [stubgen_exe, str(py_file), "-o", "src", "--include-private", "--export-less"],
                capture_output=True,
                text=True,
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
        fmt_error = "\n  ".join(str(exc).splitlines())
        print(f"[WARNING] Could not generate stubs:\n  {fmt_error}\n")


def delete_project_stub_files():
    deleted = [f for f in PROJECT_SRC.rglob("*.pyi") if f.unlink() or True]
    print(f"\nCleaned up {len(deleted)} stub file(s) from project directory.\n")


ext_modules = []

# Only compile and generate stubs when actually building, not during metadata-only
# phases (egg_info, dist_info) that pip invokes as part of PEP 517 preparation.
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

    except (ImportError, Exception) as e:
        fmt_error = "\n  ".join(str(e).splitlines())
        print(
            f"\n[WARNING] mypyc compilation disabled (not available or failed):\n  {fmt_error}\n"
            "\nInstalling as pure Python package...\n"
        )

setup(
    name="xulbux",
    ext_modules=ext_modules,
)

if _is_building:
    delete_project_stub_files()
