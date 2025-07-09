# Burnout Web

## Install

With Python 3.8

```
python -m venv .venv
# Linux
.venv/bin/activate
# Windows
.venv\Scripts\Activate.ps1

cd app
pip install -e .
```

Download wheel for Linux or Windows from https://gitlab.kitware.com/kwiver/kwiver/-/packages/442

Alternatively, the build scripts use these direct wheel URLs:
- Linux: https://data.kitware.com/api/v1/item/686be6a0132a72f109c1bb9b/download
- Windows: https://data.kitware.com/api/v1/item/686be762132a72f109c1bb9e/download

```
# with trame app venv active
pip install kwiver_*.whl
burn-out --use-tk
```

## Development

### Releases and Tags

**Automatic Releases:**
- Merge to `master` branch triggers semantic-release
- Creates Git tag and GitHub release with built artifacts

**Manual Releases:**
- Use GitHub Actions "Run workflow" with "Create a GitHub release" option
- Creates release with tag `manual-{run_number}`
