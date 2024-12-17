## Overview

`pytest-history` enables the tracking of test statuses and other metadata across multiple test runs, providing
additional insights into test behavior.

## Usage

## Configuration Options

To enable test history reporting to Supabase, you'll need to provide authentication credentials using any of these methods:

#### Environment Variables
```bash
export PYTEST_HISTORY_EMAIL=your.email@example.com
export PYTEST_HISTORY_PASSWORD=your-password
```

#### Command-line Parameters
```bash
pytest --history-email your.email@example.com --history-password your-password tests/
```

#### INI File Setting (Email Only)
```ini
# pytest.ini
[pytest]
history-email = your.email@example.com
```

```toml
# pyproject.toml
[tool.pytest.ini_options]
history-email = "your.email@example.com"
```

Note: For security reasons, the password can only be provided via environment variable or command-line parameter.

When multiple configuration methods are used simultaneously, command-line parameters take precedence over environment variables, which take precedence over INI file settings.

# Credits

Based on [pytest-history](https://github.com/Nicoretti/one-piece/tree/grand-line/python/pytest-history) by Nicola Coretti.
