#!/bin/bash
# =============================================================================
# DJANGO BOILERPLATE - Requirements Installation Script
# =============================================================================
# Description: Install/update all Python dependencies
# Usage: ./docs/bash/requirements.sh (from any directory)
# =============================================================================

set -e  # Exit on error

# Get the project root directory (2 levels up from docs/bash/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"
echo "📁 Working in: $PROJECT_ROOT"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Error: Virtual environment not found. Run setup.sh first."
    exit 1
fi

echo ""
echo "=========================================="
echo "   INSTALLING REQUIREMENTS"
echo "=========================================="
echo ""

# Upgrade pip first
echo "🔧 Upgrading pip..."
pip install --upgrade pip

echo ""
echo "🔧 Installing requirements from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "   ✅ REQUIREMENTS INSTALLED!"
echo "=========================================="
echo ""

# Show installed packages
echo "📦 Installed packages:"
pip list
echo ""
