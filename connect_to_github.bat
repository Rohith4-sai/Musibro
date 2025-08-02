@echo off
echo 🚀 Connecting to GitHub...
echo.

echo Please follow these steps:
echo 1. Go to https://github.com and create a new repository
echo 2. Name it: music-recommendation-app
echo 3. DO NOT initialize with README, .gitignore, or license
echo 4. Copy the repository URL
echo.

set /p GITHUB_URL="Enter your GitHub repository URL (e.g., https://github.com/username/music-recommendation-app.git): "

echo.
echo Adding remote repository...
git remote add origin %GITHUB_URL%

echo.
echo Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo ✅ Success! Your repository is now on GitHub!
echo.
pause 