# Sovereign Shift: Monday Audit Cycle
# This script automates the transition from individual data to the collective Trust report.

Write-Host "--- 🏁 Initiating Sovereign Shift (Monday Cycle) ---" -ForegroundColor Cyan

# 1. Reconcile Ledger (The "Debt to Trust" Transition)
Write-Host "[1/3] Reconciling Ledger..." -ForegroundColor Yellow
python scripts/reconcile_ledger.py

# 2. Generate Transparency Report
Write-Host "[2/3] Generating Monday Report..." -ForegroundColor Yellow
python scripts/generate_monday_report.py

# 3. Synchronize with Sovereign Vault (GitHub)
Write-Host "[3/3] Committing Audit Results..." -ForegroundColor Yellow
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss UTC"
git add data/internal_ledger.json
git add data/reports/monday_report_latest.md
git commit -m "Sovereign Audit: Monday Cycle Completed at $Timestamp"
git push

Write-Host "--- ✅ Shift Complete. Transparency Portal Updated. ---" -ForegroundColor Green
