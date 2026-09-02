---
name: test-xulbux
description: Strict guidelines and commands for running tests and maintaining 100% test coverage in the xulbux library.
---

# test-xulbux

Use this skill to create, organize, run, and maintain tests in the `xulbux` library. Test coverage must always be exactly **100%** on both Windows and Unix (Linux / macOS), and all tests must be clean, logically organized, and maintainable.

---

## 1. Test Directory & File Architecture

Tests are structured cleanly to mirror the `src/xulbux/` layout:

1.  **Module Folder Mapping:** Every module in `src/xulbux/` corresponds to a matching directory in `tests/test_<module>/` (e.g., `tests/test_ansi/`, `tests/test_color/`, `tests/test_console/`, `tests/test_data/`, `tests/test_system/`, `tests/test_file_sys/`).
2.  **Domain-Driven Separation:** Split tests by core responsibility, class, or feature domain rather than artificial "normal vs edge-case" splits.
    *   *Example:* In `tests/test_color/`: `test_rgba.py`, `test_hsla.py`, `test_hexa.py`, `test_conversions.py`, `test_color_utils.py`.
    *   *Example:* In `tests/test_console/`: `test_progress.py`, `test_throbber.py`, `test_arg_parser.py`, `test_log_box.py`, `test_terminal_and_prompts.py`.
3.  **No Monolithic Files:** Do NOT dump all tests of a large module into a single giant file. Group related classes/functions logically into targeted test files.
4.  **Cross-Module Consistency:** Keep naming and structural patterns consistent across all module test suites.

---

## 2. Test Function Naming & Cleanliness

1.  **Naming Pattern:** Always use descriptive names following the pattern:

    ```python
    test_<function_or_method>_<expected_behavior_or_outcome>()
    ```

    *Examples:*
    *   `test_format_table_with_custom_headers()`
    *   `test_rgba_from_hex_invalid_length_raises_value_error()`
    *   `test_has_color_support_windows_vt_mode_disabled()`
    *   `test_resolve_path_missing_paths()`
2.  **Zero Duplication:** Consolidate repetitive assertions into `@pytest.mark.parametrize` tables or clean helper fixtures instead of duplicating test functions.
3.  **No Agent Monologue or Notes:** Test files must contain only clean, readable code. Never include conversational notes, agent thoughts, or messy comment chatter.
4.  **Comments & Separators:**
    *   If section separators are used in test files, format them as 127-character-wide uppercase header bars:

        ```python
        # ****************************************************** Throbber TESTS *******************************************************
        ```

    *   Tests should be self-explanatory from their directory, file, and function names. Keep inline comments minimal and focused.
5.  **Type Ignore Formatting:** When using `# pyright:ignore[…]` or `# type:ignore[…]`, **NEVER** put spaces after commas between rule names (e.g., `# pyright:ignore[attr-defined,reportUnknownMemberType]`).

---

## 3. Cross-Platform Reliability (Windows & Unix)

All tests must pass on **both Windows and Unix** without platform-dependent crashes:

1.  **Safely Mock Windows-Only Modules (`ctypes.windll`, `msvcrt`):**
    *   On Linux/macOS, `ctypes` has no `windll` attribute and `msvcrt` does not exist.
    *   For `ctypes.windll`: Use the `mock_ctypes_windll` fixture from `conftest.py` or mock on `ctypes` with `raising=False`. Never do direct `patch("ctypes.windll.…")`.
    *   For `msvcrt`: Use `patch.dict("sys.modules", {"msvcrt": mock_msvcrt})` instead of direct `patch("msvcrt.getch")`.
2.  **`pathlib.Path` on Unix:**
    *   Python 3.14+ prevents instantiating `WindowsPath` on POSIX systems.
    *   Do NOT monkeypatch `os.name = "nt"` when testing functions that call `pathlib.Path.resolve()` or instantiate paths. Instead, monkeypatch `sys.platform = "win32"` if the tested code only branches on `sys.platform`.
3.  **Cover Both Platform Branches:**
    *   Always ensure both Windows (`nt`, `win32`, drive letters) and POSIX (`posix`, `linux`, `darwin`, root slashes) code branches are tested so 100% coverage is achieved on any OS.

---

## 4. Coding Standards & MyPyC Idioms in Tests

-   **Strict Typing:** All test functions, fixtures, and helpers must be fully type-hinted (`def test_…() -> None:`).
-   **No Generator Expressions in Iteration Builtins:** Never pass generator expressions to `any()`, `all()`, `sum()`, `max()`, `min()`, `join()`, `tuple()`. Use list comprehensions `[…]` or unrolled loops.
-   **Descriptive Variable Names:** No single-letter variable names (except `i`, `j` for loop indices and `n` for counts/math).

---

## 5. Running Linters & Tests

### On Unix (Linux / macOS)

CD into the project root, activate `.venv`, and run:

```bash
ruff format . && ruff check . --fix && pyright --pythonpath .venv/bin/python . && mypy . && pytest -q --disable-warnings
```

### On Windows

CD into the project root and run:

```powershell
ruff format . ; if ($?) { ruff check . --fix } ; if ($?) { pyright --pythonpath "$(py -c 'import sys; print(sys.executable)')" . } ; if ($?) { mypy . } ; if ($?) { pytest --basetemp .pytest_tmp -q --disable-warnings }
```

---

## 6. Resolving Missing Coverage & Bugs

-   **Check Missing Lines:** Coverage reports list exact line numbers that were not hit.
-   **Write Targeted Tests:** Add tests specifically exercising unexecuted branches or exception blocks.
-   **Fix Code Bugs:** If a line cannot be covered or fails due to a real bug in `src/xulbux/`, **fix the bug in the code**. Never write tests expecting broken behavior.
-   **No Pragmas Unless Truly Unavoidable:** Do not use `# pragma:no-cover` unless strictly necessary for defensive type-checking blocks already configured in `pyproject.toml`.

---

## 7. Mutation Testing (Mutmut)

Use `mutmut` for periodic or on-demand test quality audits to catch redundant or ineffective tests.

### Run Mutation Testing:

-   **Run on a specific module or file:**

    ```bash
    mutmut run src/xulbux/ansi.py
    ```

-   **Inspect results & surviving mutants:**

    ```bash
    mutmut results
    mutmut show <mutant_id>
    ```
