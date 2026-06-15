param(
  [switch]$NoPull,
  [string]$Destination = "",
  [string]$EmailTo = ""
)

$ErrorActionPreference = "Stop"
$DbFile = "ehealth_malawi.db"

# stop any running server on port 8000 so the DB isn't locked
Write-Host "[!] Stopping all Python processes on port 8000..." -ForegroundColor Yellow
Get-Process -Name "python*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
# verify port is free
$stillRunning = netstat -ano | Select-String ":8000 " | Select-String "LISTENING"
if ($stillRunning) { Write-Host "[-] Port 8000 still in use - close it manually (Ctrl+C in the server terminal)" -ForegroundColor Red }

# load .env vars
if (Test-Path ".env") {
  Get-Content ".env" -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()
    if ($line -and $line -notmatch "^\s*#") {
      $idx = $line.IndexOf("=")
      if ($idx -gt 0) {
        $key = $line.Substring(0, $idx).Trim()
        $val = $line.Substring($idx + 1).Trim()
        [Environment]::SetEnvironmentVariable($key, $val, "Process")
      }
    }
  }
  Write-Host "[+] Loaded .env (SMTP_USER=$([Environment]::GetEnvironmentVariable('SMTP_USER','Process')))" -ForegroundColor Gray
}

# 1. backup DB — Usage:
#   external drive: .\deploy.ps1 -Destination D:\ehealth_backups
#   email inbox:    .\deploy.ps1 -EmailTo you@gmail.com
#   no args:        local ./backups/ folder
if (Test-Path $DbFile) {
  $stamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $backupName = "${stamp}_$DbFile"

  if ($Destination) {
    if (-not (Test-Path $Destination)) { New-Item -ItemType Directory -Path $Destination | Out-Null }
    Copy-Item $DbFile "$Destination\$backupName"
    Write-Host "[+] Backed up $DbFile → $Destination\$backupName" -ForegroundColor Green
  } elseif ($EmailTo) {
    $smtpUser = $env:SMTP_USER
    $smtpPass = $env:SMTP_PASS
    $smtpHost = $env:SMTP_HOST
    $smtpPort = if ($env:SMTP_PORT) { [int]$env:SMTP_PORT } else { 587 }
    if (-not $smtpUser -or -not $smtpPass) {
      Write-Host "[-] Set SMTP_USER / SMTP_PASS env vars for email backup" -ForegroundColor Red
      Write-Host "[!] Falling back to local backup" -ForegroundColor Yellow
      $Destination = "backups"
      if (-not (Test-Path $Destination)) { New-Item -ItemType Directory -Path $Destination | Out-Null }
      Copy-Item $DbFile "$Destination\$backupName"
    } else {
      # copy DB to a temp path so the file isn't locked during send
      $tmpDb = "$env:TEMP\$backupName"
      $copied = $false
      for ($i = 0; $i -lt 5; $i++) {
        try { Copy-Item $DbFile $tmpDb -Force; $copied = $true; break } catch { Start-Sleep -Seconds 1 }
      }
      if (-not $copied) {
        Write-Host "[-] Could not copy $DbFile (still locked)" -ForegroundColor Red
        Write-Host "[!] Falling back to local backup" -ForegroundColor Yellow
        $Destination = "backups"
        if (-not (Test-Path $Destination)) { New-Item -ItemType Directory -Path $Destination | Out-Null }
        Copy-Item $DbFile "$Destination\$backupName"
      } else {
        $msg = @{
          To         = $EmailTo
          From       = $smtpUser
          Subject    = "eHealth DB backup $stamp"
          Body       = "Attached is the eHealth_Malawi database backup from $stamp"
          Attachment = $tmpDb
          SmtpServer = $smtpHost
          Port       = $smtpPort
          Credential = (New-Object System.Management.Automation.PSCredential($smtpUser, (ConvertTo-SecureString $smtpPass -AsPlainText -Force)))
          UseSsl     = $true
        }
        Send-MailMessage @msg
        Remove-Item $tmpDb -Force -ErrorAction SilentlyContinue
        Write-Host "[+] Emailed $DbFile backup to $EmailTo" -ForegroundColor Green
      }
    }
  } else {
    $BackupDir = "backups"
    if (-not (Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir | Out-Null }
    Copy-Item $DbFile "$BackupDir\$backupName"
    Write-Host "[+] Backed up $DbFile → $BackupDir\$backupName" -ForegroundColor Green
  }
}

# 2. pull latest code
if (-not $NoPull) {
  Write-Host "[+] Pulling latest code..."
  $pullOut = & git pull 2>&1 | Out-String
  if ($LASTEXITCODE -ne 0) { Write-Host "[!] git pull skipped (no tracking branch configured)" -ForegroundColor Yellow }
}

# 3. install deps
Write-Host "[+] Installing requirements..."
& pip install -r requirements.txt -q
if (-not $?) { Write-Host "[-] pip install failed" -ForegroundColor Red; exit 1 }

# 4. start server
Write-Host "[+] Starting server..."
python run.py
