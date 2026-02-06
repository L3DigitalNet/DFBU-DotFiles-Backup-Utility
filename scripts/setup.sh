#!/bin/bash
# Development environment setup script for Linux
# Requires Python 3.14 and UV

set -e

echo "Setting up Template Desktop Application development environment..."

# Check if UV is installed
if ! command -v uv &>/dev/null; then
	echo "UV is not installed. Installing UV..."
	curl -LsSf https://astral.sh/uv/install.sh | sh

	# Add UV to PATH for current session
	export PATH="$HOME/.cargo/bin:$PATH"

	echo "UV installed successfully!"
fi

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Verify Python 3.14
if [[ ! "$python_version" =~ ^3\.14 ]]; then
	echo "❌ Error: Python 3.14 is required, but found $python_version"
	echo "Please install Python 3.14 and try again."
	exit 1
fi

# Create virtual environment and sync dependencies with UV
echo "Creating virtual environment and syncing dependencies..."
uv sync

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install pre-commit hooks
echo "Installing pre-commit git hooks..."
pre-commit install

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run the application:"
echo "  python -m DFBU"
echo ""
echo "To run tests:"
echo "  pytest DFBU/tests/"
echo ""
echo "To run pre-commit hooks manually:"
echo "  pre-commit run --all-files"
echo ""
echo "To run tests with coverage:"
echo "  pytest DFBU/tests/ --cov=DFBU --cov-report=html"
echo ""
