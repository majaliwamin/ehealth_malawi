Write-Host "=== eHealth Malawi Setup ===" -ForegroundColor Cyan
Write-Host "Installing Python dependencies..."
Set-Location "$PSScriptRoot\..\backend"
pip install -r requirements.txt
Write-Host "Setup complete. Run 'python run.py' to start the server." -ForegroundColor Green
