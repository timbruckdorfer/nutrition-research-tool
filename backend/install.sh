#!/bin/bash
# Installation script for Nutrition Research Tool backend

echo "==================================="
echo "Installing Nutrition Research Tool"
echo "==================================="

# Step 1: Check Python version
echo "\n1. Checking Python version..."
python3.12 --version || { echo "Python 3.12 not found. Please install Python 3.12+"; exit 1; }

# Step 2: Create virtual environment
echo "\n2. Creating virtual environment with Python 3.12..."
if [ -d "venv" ]; then
    echo "Removing old venv..."
    rm -rf venv
fi
python3.12 -m venv venv

# Step 3: Activate virtual environment
echo "\n3. Activating virtual environment..."
source venv/bin/activate

# Step 4: Upgrade pip
echo "\n4. Upgrading pip..."
pip install --upgrade pip

# Step 5: Install dependencies (except MCP)
echo "\n5. Installing Python packages..."
pip install openai pymupdf fastapi "uvicorn[standard]" python-multipart openpyxl pandas python-dotenv pydantic

# Step 6: Install MCP SDK from GitHub
echo "\n6. Installing MCP SDK from GitHub..."
pip install git+https://github.com/modelcontextprotocol/python-sdk.git

# Step 7: Verify installation
echo "\n7. Verifying installation..."
python -c "import openai; import fitz; import fastapi; import mcp; print('✓ All packages installed successfully!')"

echo "\n==================================="
echo "Installation complete!"
echo "==================================="
echo "\nNext steps:"
echo "1. Edit backend/.env and add your OpenAI API key"
echo "2. Test with: python test_mcp_server.py path/to/paper.pdf"
echo "3. Or run the MCP server: python mcp_server/server.py"
