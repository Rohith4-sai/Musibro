Write-Host "🚀 Connecting to GitHub..." -ForegroundColor Green
Write-Host ""

Write-Host "Please follow these steps:" -ForegroundColor Yellow
Write-Host "1. Go to https://github.com and create a new repository" -ForegroundColor White
Write-Host "2. Name it: music-recommendation-app" -ForegroundColor White
Write-Host "3. DO NOT initialize with README, .gitignore, or license" -ForegroundColor White
Write-Host "4. Copy the repository URL" -ForegroundColor White
Write-Host ""

$githubUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/music-recommendation-app.git)"

Write-Host ""
Write-Host "Adding remote repository..." -ForegroundColor Cyan
git remote add origin $githubUrl

Write-Host ""
Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git branch -M main
git push -u origin main

Write-Host ""
Write-Host "✅ Success! Your repository is now on GitHub!" -ForegroundColor Green
Write-Host "" 