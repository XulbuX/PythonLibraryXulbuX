# Agent Guidelines for `xulbux`

When working on this repository, any AI agent or automated assistant must adhere strictly to the following rules to maintain the codebase's integrity, performance, and correctness.

## 1. Strict Typing (MyPyC Compatibility)

This entire library (including all Python files across all subdirectories of `src/xulbux/`, such as `base/`, `cli/`, etc.) is compiled to C using **MyPyC**. Therefore, **EVERYTHING** must be meticulously and strictly type-hinted. Do not ever use `Any` unless it is fundamentally impossible to type-hint otherwise. All changes must be fully statically analyzable to compile correctly.

## 2. Validation & Testing

After making any changes, you must validate them by running the full suite of formatters, linters, type checkers, and tests. Fix all problems until they are completely resolved. Test coverage must always remain at exactly 100%. Use the `test-xulbux` skill for testing guidelines and commands, and the `build-xulbux` skill for compilation and stub generation.

## 3. Ask, Don't Assume

If you run into anything you are not sure about (ambiguous requirements, complex architectural decisions, edge cases), **ask first**. Do not make assumptions about the desired behavior.

## 4. Performance & MyPyC Idioms

*   **Performance First:** This library prioritizes modernity and speed. Avoid eager imports for heavy operations. Utilize lazy loading via PEP 562 (`__getattr__` in `__init__.py`) and lazy compiled regular expressions (`LazyRegex`).
*   **MyPyC Optimization (CRITICAL):** Because the library in its entirety (all modules and subpackages) is compiled to C via MyPyC, standard Python performance advice doesn't always apply. You must strictly follow these rules everywhere across the codebase:
    *   **Generators:** NEVER pass generator expressions to functions like `any()`, `all()`, `sum()`, `max()`, `min()`, `join()`, `tuple()`, etc.
        *   For full iterations (`join`, `sum`, `tuple`, `max`), ALWAYS wrap them in brackets `[]` to force an optimized list comprehension.
        *   For short-circuiting functions (`any`, `all`, `next`), write explicit unrolled native `for`-loops with `break` or `return`.
    *   **Membership Testing:** Always use `set`s for `in` checks instead of lists or tuples (e.g., `if x in {"a", "b"}:` instead of `if x in ("a", "b"):`).
    *   **String Concatenation:** Avoid using `+=` for string concatenation inside loops; prefer `.join()` with list comprehensions.
    *   **Map & Filter:** Do not use the `map()` or `filter()` builtins. List comprehensions are strictly faster and type-safer in MyPyC.
*   **DRY Principle (Don't Repeat Yourself):** Always strive to prevent redundant code and duplicate logic. Abstract repeated patterns into reusable helper functions or classes.
*   **Internal Module Aliasing:** When importing internal modules, use the `_module` suffix pattern (e.g., `from . import data as _data_module`). This prevents naming collisions and variable shadowing, and keeps the public API completely clean of internal clutter.

## 5. Code Structure & Readability

*   **Logical Placement:** Do not mindlessly append new code (variables, constants, functions, classes, etc.) to the end of a file. Always insert new code in a logical location that groups related functionality together.
*   **Private Constants Placement:** Private constants and module-level variables (e.g., `_PATTERNS`, caches, lookup tables) should always be defined directly below the imports at the very top of the file.
*   **Spacing & Formatting:** Keep the code "spacy" and readable, matching the current formatting conventions of the repository.
*   **Imports Placement:** Always place imports at the top of the file. The only exception is OS-specific libraries (such as `winreg`, `msvcrt`, `termios`, or `tty`) that do not exist on other operating systems and therefore must be imported inside platform-specific code branches.
*   **Explicit Import Styles:** For libraries like `typing`, `typing_extensions`, `collections.abc`, and `pathlib`, always use explicit `from <module> import ...` statements (e.g., `from typing import overload, Any`, `from pathlib import Path`). Never import the entire module as `import typing` or `import pathlib`.
*   **Naming Conventions:**
    *   **Descriptive Variable Names:** Single-letter variables (e.g., `x`, `c`, `r`) are strictly banned. The ONLY exceptions are `i` (and rarely `j`) for loop indices, and `n` for mathematical counts/parameters. Always use fully descriptive variable names (e.g., `ch` or `channel`, `red`, `modifier`).
    *   **Instance Conversions & Representations:** Instance methods that convert or represent the object in another format or representation must always use the **`as_…()`** prefix (e.g., `.as_dict()`, `.as_tuple()`, `.as_rgba()`, `.as_fg()`, `.as_text_fg()`). Never use `.to_…()` or bare data structure names like `.dict()` or `.values()`.
    *   **Standalone Conversions & Transformations:** Standalone functions should use **`to_…`** (or `…_to_…`) when actively transforming data from one format/casing/type to another (e.g., `to_camel_case()`, `to_delimited_case()`, `to_type()`, `rgba_to_hex_int()`), and **`as_…`** (or `…_as_…`) when casting or interpreting an arbitrary input object as a target concept or model (e.g., `as_rgba()`, `as_hsla()`, `as_hexa()`). Choose whichever sounds most natural and logical in context.
    *   **Extraction vs. Conversion:** Functions that search/parse values out of arbitrary text or unstructured data must use the **`extract_…`** prefix (e.g., `extract_rgba()`, `extract_hsla()`), reserving direct `to_…` / `as_…` naming strictly for direct conversions.
    *   **Verb-First for Actions & Getters:** Functions performing actions or fetching data should start with an active verb (e.g., `count_chars()`, `get_paths()`, `remove_duplicates()`).
    *   **Path Resolution:** Always use standard filesystem terminology like **`resolve_path`** and **`resolve_or_create_path`** instead of non-standard terms like `extend_path`.
    *   **Predicates & Booleans:** Predicate functions and boolean properties/methods must always start with `is_` or `has_` (e.g., `is_light()`, `has_alpha()`, `is_valid_rgba()`, `is_tty()`).
*   **Organization:** When introducing large data structures (like hardcoded iterables or dictionaries), keep them strictly organized and structured. Default to sorting elements alphabetically unless a specific logical order is required.

## 6. Documentation & Markdown Formatting

*   **Markdown Linting:** All Markdown files (`.md`) must strictly adhere to the formatting and linting rules defined in `.markdownlint.json`.
*   **Docstrings & Comments:** Follow the `docs-xulbux` skill for all docstring structure, styling, `<br>` line wraps, horizontal rules, custom docs components, and comment conventions. Numbered step comments must always use square brackets like `# [1]`, `# [2]` (never `1.`, `2.`). Always provide at least a one-line docstring for private variables, functions, and classes explaining their purpose.

## 7. Dependency Management

*   **Minimum Versions:** If you make use of a new feature from a non-dev dependency (e.g., `prompt_toolkit`, `regex`, `typing_extensions`) that isn't already used elsewhere in the library, you must check if that feature is available in the currently listed minimum version in `pyproject.toml`. If it is not, bump the minimum version of that dependency **only** to the lowest stable version where that feature was introduced, never to the absolute latest version by default.
*   **Synchronization:** If you update any dependency version in `pyproject.toml`, you must ensure that the `__dependencies__` list in `src/xulbux/__init__.py` is updated to perfectly match it.

## 8. Exports & `__init__.py`

*   **Top-level Exports:** Everything (modules and classes) should be exported in the main `src/xulbux/__init__.py` file (and therefore also listed in `__all__` and `_SUBMODULES`).
    *   **Exceptions:** Custom types (type aliases, TypedDicts, etc.) and anything inside the `base` module (like `base.exceptions` or `base.consts`) should **not** be exported to the top-level namespace to keep it clean.
