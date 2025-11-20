# Publishing Vaquero SDK to PyPI

This guide explains how to publish the `vaquero-sdk` package to PyPI so users can install it with `pip` or `uv pip`.

## Prerequisites

1. **PyPI Account**: Create an account at [pypi.org](https://pypi.org/account/register/)
2. **TestPyPI Account**: Create an account at [test.pypi.org](https://test.pypi.org/account/register/) (recommended for testing)
3. **API Tokens**: Generate API tokens for both PyPI and TestPyPI:
   - Go to Account Settings → API tokens
   - Create a new token with "Entire account" scope (or project-specific scope)
   - Save the token securely (you'll only see it once)

## Quick Start

### Option 1: Using the Publishing Script (Easiest)

```bash
cd sdk

# Test on TestPyPI first (recommended)
./publish.sh test

# After testing, publish to production PyPI
./publish.sh prod
```

The script will:
- Clean previous builds
- Build the package
- Check the package for issues
- Upload to the specified repository

### Option 2: Using Make

```bash
cd sdk

# Build the package
make build

# Test locally first
pip install dist/vaquero_sdk-*.whl

# Upload to TestPyPI (recommended first step)
make upload-test

# After testing, upload to PyPI
make upload
```

### Option 3: Manual Commands

```bash
cd sdk

# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to TestPyPI (recommended first step)
twine upload --repository testpypi dist/*

# After testing, upload to PyPI
twine upload dist/*
```

## Step-by-Step Guide

### 1. Prepare the Package

Ensure all required files are in place:

- ✅ `pyproject.toml` - Package configuration (already configured)
- ✅ `MANIFEST.in` - Files to include in distribution (already configured)
- ✅ `LICENSE` - License file (MIT License exists in root)
- ✅ `README.md` - Package documentation (already exists)
- ✅ `CHANGELOG.md` - Change history (exists in root directory)

**Note**: The `LICENSE` file is in the project root. The `MANIFEST.in` should include it. Let's verify:

```bash
cd sdk
cat MANIFEST.in
```

If `LICENSE` isn't in `MANIFEST.in`, you may need to copy it to the `sdk/` directory or update `MANIFEST.in`.

### 2. Update Version Number

Before publishing, update the version in `pyproject.toml`:

```toml
[project]
version = "0.1.0"  # Update this to your new version
```

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.2.0): New features, backward compatible
- **PATCH** (0.1.1): Bug fixes, backward compatible

### 3. Update CHANGELOG

Update `CHANGELOG.md` with your changes:

```markdown
## [0.1.1] - 2025-01-XX

### Fixed
- Fixed issue with batch processing
- Improved error handling

### Changed
- Updated dependencies
```

### 4. Clean Previous Builds

```bash
cd sdk
make clean
# Or manually:
rm -rf build/ dist/ *.egg-info/
```

### 5. Build the Package

```bash
cd sdk

# Install build tools if not already installed
pip install build twine

# Build source distribution and wheel
python -m build
```

This creates:
- `dist/vaquero_sdk-<version>.tar.gz` - Source distribution
- `dist/vaquero_sdk-<version>-py3-none-any.whl` - Wheel distribution

### 6. Verify the Package

```bash
# Check package for common issues
twine check dist/*

# Test install locally
pip install dist/vaquero_sdk-*.whl --force-reinstall

# Verify it works
python -c "import vaquero; print(vaquero.__version__)"
```

### 7. Test on TestPyPI (Recommended)

**First-time setup for TestPyPI:**

```bash
# Create ~/.pypirc file (optional, for convenience)
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-token>

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = <your-pypi-token>
EOF
chmod 600 ~/.pypirc
```

**Upload to TestPyPI:**

```bash
cd sdk

# Upload using token (recommended)
twine upload --repository testpypi dist/* \
  --username __token__ \
  --password <your-testpypi-api-token>
```

**Test installation from TestPyPI:**

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ vaquero-sdk

# Or with uv
uv pip install --index-url https://test.pypi.org/simple/ vaquero-sdk
```

### 8. Publish to PyPI

Once you've verified the package on TestPyPI:

```bash
cd sdk

# Upload to PyPI
twine upload dist/* \
  --username __token__ \
  --password <your-pypi-api-token>
```

**Or using environment variables (more secure):**

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your-pypi-api-token>
twine upload dist/*
```

### 9. Verify Publication

After publishing, verify the package is available:

```bash
# Wait a few minutes for PyPI to update, then:
pip install vaquero-sdk

# Or with uv
uv pip install vaquero-sdk

# Verify version
python -c "import vaquero; print(vaquero.__version__)"
```

Check the package page: https://pypi.org/project/vaquero-sdk/

## Using uv pip

`uv` is a fast Python package installer. Users can install your package with:

```bash
# Install from PyPI
uv pip install vaquero-sdk

# Install with optional dependencies
uv pip install "vaquero-sdk[all]"

# Install specific version
uv pip install vaquero-sdk==0.1.0
```

No special configuration is needed - if your package is on PyPI, `uv pip` can install it automatically.

## Automated Publishing with GitHub Actions

The project includes GitHub Actions workflows for automated publishing. See `.github/workflows/sdk.yml` for the configuration.

To use automated publishing:

1. Add PyPI API token to GitHub Secrets:
   - Go to Repository Settings → Secrets and variables → Actions
   - Add secret: `PYPI_API_TOKEN` with your PyPI API token
   - Add secret: `TEST_PYPI_API_TOKEN` with your TestPyPI API token

2. Create a GitHub Release:
   - The workflow automatically publishes when you create a release
   - Tag format: `v0.1.0` (matches version in `pyproject.toml`)

## Troubleshooting

### "Package already exists" Error

If you try to upload the same version twice, PyPI will reject it. You must:
- Increment the version in `pyproject.toml`
- Rebuild the package
- Upload again

### "Invalid distribution" Error

Make sure you're uploading both files:
```bash
twine upload dist/*
```

Not just one file.

### Authentication Issues

- Use `__token__` as username (not your PyPI username)
- Use the API token as password (not your PyPI password)
- Ensure the token has the correct scope (project-specific or entire account)

### Missing Files in Distribution

Check `MANIFEST.in` includes all necessary files:
- README.md
- LICENSE
- CHANGELOG.md
- All Python files in `vaquero/` directory

## Best Practices

1. **Always test on TestPyPI first** - Catch issues before publishing to production
2. **Use semantic versioning** - Follow MAJOR.MINOR.PATCH format
3. **Update CHANGELOG** - Document all changes for users
4. **Tag releases in Git** - Create a git tag matching the version
5. **Test installation** - Verify the package installs correctly after publishing
6. **Use API tokens** - More secure than username/password
7. **Keep tokens secret** - Never commit tokens to version control

## Version Management

After publishing, create a git tag:

```bash
git tag v0.1.0
git push origin v0.1.0
```

This helps users find the exact code for each published version.

## Next Steps

After publishing:

1. Update documentation with installation instructions
2. Announce the release (if applicable)
3. Monitor PyPI statistics and user feedback
4. Plan the next release

## Resources

- [PyPI Documentation](https://packaging.python.org/en/latest/guides/distributing-packages-using-setuptools/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging User Guide](https://packaging.python.org/)

