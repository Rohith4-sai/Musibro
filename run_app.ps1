Write-Host "🎵 Starting Music Recommendation App with Python 3.11..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
& ".\venv311\Scripts\Activate.ps1"

# Verify Python version
Write-Host "🐍 Python Version:" -ForegroundColor Cyan
python --version

Write-Host ""
Write-Host "🚀 Starting Streamlit app..." -ForegroundColor Green
streamlit run app.py 