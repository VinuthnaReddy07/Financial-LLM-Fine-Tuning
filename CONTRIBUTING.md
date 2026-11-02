# Contributing

Thank you for your interest in improving this research project.

## Set up the environment

Use Python 3.11 or newer. From the repository root, create a virtual environment
and install the project with its development dependencies:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -e ".[dev]"
```

Install a machine-appropriate PyTorch build first if you need a specific CUDA
version.

## Validate changes

Run the test suite before opening a pull request:

```powershell
.\venv\Scripts\python.exe -m pytest
```

GitHub Actions runs the same suite for pushes and pull requests. Include tests
for behavior changes and update relevant documentation.

## Project boundaries

- Keep model-generated financial explanations clearly labeled as unverified.
- Do not describe this project as validated financial advice or suitable for
  consequential decisions.
- Keep the API bound to loopback unless authentication and deployment security
  are deliberately addressed.
- Preserve source datasets, checkpoints, and prior reports; use new output paths
  for generated artifacts.
- Do not commit credentials, private user data, local model weights, or generated
  experiment checkpoints.
