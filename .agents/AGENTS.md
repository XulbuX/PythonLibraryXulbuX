# Agent Guidelines for `xulbux`

When working on this repository, any AI agent or automated assistant must adhere strictly to the following rules to maintain the codebase's integrity, performance, and correctness.

## 1. Strict Typing (MyPyC Compatibility)

This library is compiled using **MyPyC**. Therefore, **EVERYTHING** must be typed extremely strictly and accurately. Do not use `Any` unless absolutely unavoidable. All changes must be fully statically analyzable to compile correctly.

## 2. Validation & Testing

After making any changes, you must validate them by running the full suite of formatters, linters, type checkers, and tests. Fix all problems until they are completely resolved.

**On Windows:**

CD into the project root, then run:

```powershell
ruff format .; if ($?) { ruff check . --fix }; if ($?) { pyright --pythonpath "$(py -c 'import sys; print(sys.executable)')" . }; if ($?) { mypy . }; if ($?) { pytest }
```

**On Unix:**

CD into the project root, activate the `.venv` virtual environment, then run:

```bash
ruff format . && ruff check . --fix && pyright . && mypy . && pytest
```

## 3. Ask, Don't Assume

If you run into anything you are not sure about (ambiguous requirements, complex architectural decisions, edge cases), **ask first**. Do not make assumptions about the desired behavior.

## 4. Performance & Idioms

-   **Performance First:** This library prioritizes modernity and speed. Avoid eager imports for heavy operations. Utilize lazy loading via PEP 562 (`__getattr__` in `__init__.py`) and lazy compiled regular expressions (`LazyRegex`).
-   **DRY Principle (Don't Repeat Yourself):** Always strive to prevent redundant code and duplicate logic. Abstract repeated patterns into reusable helper functions or classes.
-   **Internal Module Aliasing:** When importing internal modules, use the `_module` suffix pattern (e.g., `from . import data as _data_module`). This prevents naming collisions and variable shadowing, and keeps the public API completely clean of internal clutter.
-   **Docstrings & Syntax:** Maintain the current comment/docstring styling (which makes use of formatting elements like `<br>`). Always use backticks (`` ` ``) instead of quotes when mentioning literals, expressions, types, or variables within comments/docstrings.

## 5. Code Structure & Readability

-   **Logical Placement:** Do not mindlessly append new code (variables, constants, functions, classes, etc.) to the end of a file. Always insert new code in a logical location that groups related functionality together.
-   **Spacing & Formatting:** Keep the code "spacy" and readable, matching the current formatting conventions of the repository.
-   **Organization:** When introducing large data structures (like hardcoded iterables or dictionaries), keep them strictly organized and structured. Default to sorting elements alphabetically unless a specific logical order is required.
