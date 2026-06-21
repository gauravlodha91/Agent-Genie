# Code Quality Setup Guide

This project uses modern Python tooling to automatically:

- Format code consistently
- Detect bugs before runtime
- Validate type hints
- Organize imports
- Enforce coding standards
- Provide a single command to validate the entire codebase

---

# Why Do We Need These Tools?

Without code quality tools:

- Every developer formats code differently
- Bugs are discovered only at runtime
- Imports become messy
- Type-related errors appear in production
- Code reviews become slower

These tools automate those checks.

---

# Tools Used

## Ruff

Ruff is an extremely fast Python linter and formatter.

Think of Ruff as:

- Flake8
- isort
- pyupgrade
- many linting plugins

combined into a single tool.

### What Ruff Checks

Example:

```python
import os
import json
```

If `json` is never used:

```text
F401 'json' imported but unused
```

---

### Import Sorting

Before:

```python
from fastapi import FastAPI
import os
from pathlib import Path
```

After Ruff:

```python
import os
from pathlib import Path

from fastapi import FastAPI
```

---

### Code Formatting

Before:

```python
name="John"
print(  name )
```

After:

```python
name = "John"
print(name)
```

---

### Fix Issues Automatically

```bash
poetry run ruff check . --fix
```

or

```bash
poetry run poe fix
```

---

# MyPy

MyPy performs static type checking.

It checks code before execution.

---

## Example

Bad code:

```python
def add(a: int, b: int) -> int:
    return "hello"
```

MyPy:

```text
error: Incompatible return value type
```

---

## Another Example

```python
def greet(name: str) -> None:
    print(name)

greet(123)
```

MyPy:

```text
error: Argument 1 has incompatible type "int"
```

---

## Benefits

MyPy catches:

- Wrong return types
- Wrong function arguments
- Missing type hints
- Optional None issues
- Invalid object access

before running your application.

---

# Poe the Poet

Poe allows multiple commands to be grouped into a single command.

Instead of:

```bash
ruff format .
ruff check .
mypy .
```

You can run:

```bash
poetry run poe check
```

---

# Configuration

## Ruff

```toml
[tool.ruff]
line-length = 125
target-version = "py312"
```

### line-length

Maximum line length allowed.

Example:

```toml
line-length = 125
```

Lines longer than 125 characters will raise warnings.

---

### target-version

Specifies the Python version.

```toml
target-version = "py312"
```

This enables Python 3.12 specific checks.

---

# Ruff Lint Rules

```toml
[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
```

---

## E

Pycodestyle rules.

Example:

```python
x=1
```

Should be:

```python
x = 1
```

---

## F

Pyflakes rules.

Detects:

- unused imports
- undefined variables
- unreachable code

---

## I

Import sorting.

Automatically organizes imports.

---

## B

Bugbear rules.

Detects common mistakes.

Example:

```python
def test(items=[]):
```

Mutable default arguments can create bugs.

---

## UP

Pyupgrade rules.

Modernizes Python code.

Example:

Before:

```python
"%s" % name
```

After:

```python
f"{name}"
```

---

# Ignored Rules

```toml
ignore = ["B008"]
```

---

## Why Ignore B008?

FastAPI commonly uses:

```python
from fastapi import File

file = File(...)
```

Bugbear incorrectly flags this pattern.

Ignoring B008 prevents false positives.

---

# Ruff Formatting

```toml
[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

---

## quote-style

Always use:

```python
"name"
```

instead of:

```python
'name'
```

---

## indent-style

Use spaces instead of tabs.

---

# MyPy Configuration

```toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true
```

---

## strict = true

Enables strict type checking.

Recommended for production projects.

---

## warn_return_any

Detects:

```python
def get_user():
    ...
```

returning unknown types.

---

## disallow_untyped_defs

Forces:

```python
def get_user(user_id: int) -> dict:
```

instead of:

```python
def get_user(user_id):
```

---

## check_untyped_defs

Checks function bodies even if annotations are missing.

---

# Poe Tasks

## Fix

```toml
fix.shell = """
ruff format .
ruff check . --fix
"""
```

Runs:

1. Formatter
2. Auto-fix lint issues

Command:

```bash
poetry run poe fix
```

---

## Check

```toml
check.shell = """
ruff format . --check
ruff check .
mypy .
"""
```

Runs:

1. Format validation
2. Lint validation
3. Type checking

Command:

```bash
poetry run poe check
```

---

## Validate

```toml
validate.sequence = [
    "fix",
    "check",
]
```

Runs:

1. Auto-fix code
2. Validate everything

Command:

```bash
poetry run poe validate
```

---

# Daily Workflow

## Before Writing Code

Pull latest changes.

```bash
git pull
```

---

## During Development

Run:

```bash
poetry run poe fix
```

This automatically cleans code.

---

## Before Commit

Run:

```bash
poetry run poe check
```

Ensure:

```text
All checks passed!
```

---

## Before Push

Run:

```bash
poetry run poe validate
```

---

# Common MyPy Errors

---

## Missing Return Type

Bad:

```python
def startup():
```

Good:

```python
def startup() -> None:
```

---

## Optional None Error

Bad:

```python
file_path = config.get("path")

Path(file_path)
```

Good:

```python
file_path = config.get("path")

if file_path is None:
    raise ValueError("Missing path")

Path(file_path)
```

---

## Wrong Return Type

Bad:

```python
def add(a: int, b: int) -> int:
    return "hello"
```

Good:

```python
def add(a: int, b: int) -> int:
    return a + b
```

---

# Common Ruff Errors

---

## Unused Import

Bad:

```python
import json
```

Unused.

Remove it.

---

## Import Order

Bad:

```python
from fastapi import FastAPI
import os
```

Good:

```python
import os

from fastapi import FastAPI
```

---

# Recommended Workflow

Most developers only need:

```bash
poetry run poe fix
```

while coding and:

```bash
poetry run poe check
```

before committing.

These two commands keep the codebase clean, consistent, and production-ready.

# Final Toml File

```toml
[dependency-groups]
dev = [
    "mypy>=1.18.2",
    "poethepoet>=0.46.0",
    "ruff>=0.13.2",
    "pytest>=8.4.2",
]

# --------------------------------------------------
# Ruff Configuration
# --------------------------------------------------

[tool.ruff]
line-length = 125
target-version = "py312"

exclude = [
    ".venv",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    "scratch.ipynb",
    "*copy*.py",
]

[tool.ruff.lint]
select = [
    "E",   # pycodestyle
    "F",   # pyflakes
    "I",   # import sorting
    "B",   # bugbear
    "UP",  # pyupgrade
]

# FastAPI File(...) false positive
ignore = ["B008"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

# --------------------------------------------------
# MyPy Configuration
# --------------------------------------------------

[tool.mypy]
python_version = "3.12"

# Type checking
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true

# Package resolution
explicit_package_bases = true
mypy_path = "."

# Ignore generated / scratch files
exclude = [
    "^test/",
    "^scratch\\.ipynb$",
    ".*copy.*\\.py$",
]

# --------------------------------------------------
# Pytest
# --------------------------------------------------

[tool.pytest.ini_options]
testpaths = ["test"]

# --------------------------------------------------
# Poe Tasks
# --------------------------------------------------

[tool.poe.tasks]

# Format code only
format = "ruff format ."

# Lint only
lint = "ruff check ."

# Type checking only
types = "mypy ."

# Run tests only
test = "pytest"

# Auto-fix everything possible
fix.shell = """
ruff format .
ruff check . --fix
"""

# Full validation
check.shell = """
ruff format . --check
ruff check .
mypy .
"""

# Fix + validate
validate.sequence = [
    "fix",
    "check",
]

```

commands to run

```bash
poetry run poe format
poetry run poe fix
poetry run poe lint
poetry run poe types
poetry run poe test
poetry run poe check
poetry run poe validate
```
