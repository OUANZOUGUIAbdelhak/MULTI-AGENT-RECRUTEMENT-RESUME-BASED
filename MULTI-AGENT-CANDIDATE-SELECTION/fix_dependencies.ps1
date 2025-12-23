# PowerShell script to fix dependency issues
Write-Host "Fixing dependency conflicts..." -ForegroundColor Green

# Uninstall conflicting packages
Write-Host "`nUninstalling conflicting packages..." -ForegroundColor Yellow
pip uninstall torch torchvision transformers sentence-transformers -y

# Install compatible versions
Write-Host "`nInstalling compatible versions..." -ForegroundColor Yellow
pip install "torch>=2.0.0,<2.5.0"
pip install "torchvision>=0.15.0,<0.20.0"
pip install "transformers>=4.35.0,<5.0.0"
pip install "sentence-transformers>=2.3.0,<3.0.0"

# Install other dependencies
Write-Host "`nInstalling other dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Yellow
python -c "import torch; import torchvision; import transformers; print('✅ All imports successful!')"

Write-Host "`n✅ Dependencies fixed! You can now run the app with:" -ForegroundColor Green
Write-Host "   streamlit run src/app/app.py" -ForegroundColor Cyan
Write-Host "   or" -ForegroundColor Cyan
Write-Host "   python run.py" -ForegroundColor Cyan

