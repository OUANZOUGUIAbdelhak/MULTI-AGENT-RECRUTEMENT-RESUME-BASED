# Fix Dependency Issues

## Problem
You're getting a `RuntimeError: operator torchvision::nms does not exist` error due to version incompatibilities between PyTorch, torchvision, and transformers.

## Solution

### Step 1: Reinstall dependencies with compatible versions

```bash
# Uninstall conflicting packages
pip uninstall torch torchvision transformers sentence-transformers -y

# Install compatible versions
pip install torch>=2.0.0,<2.5.0
pip install torchvision>=0.15.0,<0.20.0
pip install transformers>=4.35.0,<5.0.0
pip install sentence-transformers>=2.3.0,<3.0.0

# Install other dependencies
pip install -r requirements.txt
```

### Step 2: Run the application correctly

**DO NOT run the app directly with Python!** Use Streamlit instead:

```bash
# Option 1: Using the run script
python run.py

# Option 2: Using Streamlit directly
streamlit run src/app/app.py

# Option 3: On Windows, double-click run.bat
```

### Step 3: Verify installation

```bash
python -c "import torch; import torchvision; import transformers; print('All imports successful!')"
```

## Alternative: Use CPU-only versions (lighter)

If you don't need GPU support:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install transformers sentence-transformers
```

## Troubleshooting

If you still get errors:

1. **Create a fresh virtual environment:**
   ```bash
   python -m venv venv_new
   source venv_new/bin/activate  # Windows: venv_new\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Check Python version:** Requires Python 3.9+

3. **Clear pip cache:**
   ```bash
   pip cache purge
   ```

