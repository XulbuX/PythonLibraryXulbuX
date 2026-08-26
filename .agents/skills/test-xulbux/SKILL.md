---
name: test-xulbux
description: Strict guidelines and commands for running tests and maintaining 100% test coverage in the xulbux library.
---

# test-xulbux

Use this skill to run tests, calculate coverage, and debug test failures in the `xulbux` library. Test coverage must always be 100%.

## 1. Test Structure

Tests are organized recursively in the `tests/` directory. Large modules have their tests split into logical subdirectories.
For example, tests for `src/xulbux/console.py` might be split into `tests/console/test_arg_parsing.py`, `tests/console/test_progress.py`, etc.
Always adhere to this structure and create smaller, well-named test files rather than monolithic `test_module.py` files.

## 2. Running Tests with Coverage

Run the following command to execute all tests and print a coverage report indicating missing lines. The build process requires exactly 100% coverage (`--cov-fail-under=100`).

**On Windows:**

```powershell
pytest --basetemp .pytest_tmp -q --disable-warnings
```

(Coverage arguments are automatically loaded from `pyproject.toml`'s `[tool.pytest.ini_options]`).

**On Unix:**

```bash
pytest -q --disable-warnings
```

## 3. Resolving Missing Coverage & Bugs

- **Check the Report:** The coverage report (`Missing` column) lists exact line numbers that were not executed during testing.
- **Write Targeted Tests:** Add tests specifically designed to trigger those unexecuted lines (e.g. testing specific edge cases, error raises, or `if/else` branches).
- **Fix Underlying Bugs:** If you discover that the reason a line isn't covered or a test is failing is due to an actual bug in the code, **fix the bug in the code**. Do NOT write a test that expects incorrect behavior just to satisfy coverage.
- **No Pragmas unless Necessary:** Do not use `# pragma:no-cover` to bypass coverage unless absolutely technically necessary (e.g. OS-specific code that cannot be mocked, or defensive type checking blocks already ignored in `pyproject.toml`).
