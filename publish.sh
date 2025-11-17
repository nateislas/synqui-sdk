#!/bin/bash
# Publishing script for vaquero-sdk
# Usage: ./publish.sh [test|prod]

set -e  # Exit on error

REPO="${1:-test}"  # Default to test

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Vaquero SDK Publishing Script${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Please run this script from the sdk/ directory.${NC}"
    exit 1
fi

# Check for required tools
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Error: python3 or python not found. Please install Python.${NC}"
        exit 1
    fi
fi

# Install build tools if needed
if ! $PYTHON_CMD -m build --version &> /dev/null 2>&1; then
    echo -e "${YELLOW}Installing build tools...${NC}"
    $PYTHON_CMD -m pip install build twine
fi

# Clean previous builds
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build/ dist/ *.egg-info/

# Build the package
echo -e "${YELLOW}Building package...${NC}"
$PYTHON_CMD -m build

# Check the package
echo -e "${YELLOW}Checking package...${NC}"
$PYTHON_CMD -m twine check dist/*

if [ $? -ne 0 ]; then
    echo -e "${RED}Package check failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Package built and checked successfully!${NC}"
echo ""

# Show package files
echo -e "${GREEN}Package files:${NC}"
ls -lh dist/

echo ""

# Upload based on repository
if [ "$REPO" = "test" ]; then
    echo -e "${YELLOW}Uploading to TestPyPI...${NC}"
    echo "You'll be prompted for credentials."
    echo "Username: __token__"
    echo "Password: Your TestPyPI API token"
    echo ""
    $PYTHON_CMD -m twine upload --repository testpypi dist/*
    echo ""
    echo -e "${GREEN}✓ Uploaded to TestPyPI!${NC}"
    echo ""
    echo "Test installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ vaquero-sdk"
    echo "  uv pip install --index-url https://test.pypi.org/simple/ vaquero-sdk"
elif [ "$REPO" = "prod" ]; then
    echo -e "${RED}⚠️  Uploading to PRODUCTION PyPI...${NC}"
    read -p "Are you sure you want to publish to PyPI? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Publishing cancelled."
        exit 0
    fi
    echo ""
    echo "You'll be prompted for credentials."
    echo "Username: __token__"
    echo "Password: Your PyPI API token"
    echo ""
    $PYTHON_CMD -m twine upload dist/*
    echo ""
    echo -e "${GREEN}✓ Uploaded to PyPI!${NC}"
    echo ""
    echo "Package available at: https://pypi.org/project/vaquero-sdk/"
    echo ""
    echo "Install with:"
    echo "  pip install vaquero-sdk"
    echo "  uv pip install vaquero-sdk"
else
    echo -e "${RED}Error: Invalid repository. Use 'test' or 'prod'${NC}"
    echo "Usage: ./publish.sh [test|prod]"
    exit 1
fi

