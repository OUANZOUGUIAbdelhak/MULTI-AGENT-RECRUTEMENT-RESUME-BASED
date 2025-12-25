#!/bin/bash

echo "========================================"
echo "Multi-Agent Candidate Selection System"
echo "Quick Start Script"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
echo ""
echo "Checking dependencies..."
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "Python dependencies already installed."
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Choose an option:"
echo "1. Start Backend API (for React frontend)"
echo "2. Start Streamlit Interface"
echo "3. Install Frontend Dependencies"
echo "4. Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Starting Backend API..."
        echo "Backend will be available at http://localhost:8000"
        echo ""
        python backend_api.py
        ;;
    2)
        echo ""
        echo "Starting Streamlit Interface..."
        echo "Interface will be available at http://localhost:8501"
        echo ""
        streamlit run src/app/app.py
        ;;
    3)
        echo ""
        echo "Installing Frontend Dependencies..."
        cd frontend
        npm install
        cd ..
        echo ""
        echo "Frontend dependencies installed!"
        echo "Run 'npm run dev' in the frontend folder to start the frontend."
        ;;
    4)
        echo ""
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac

