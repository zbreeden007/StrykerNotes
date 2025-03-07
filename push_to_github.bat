@echo off
echo === PUSH CODE CHANGES TO GITHUB ===

echo Current directory: %cd%
echo.

echo Adding all files...
git add .

echo.
set /p commit_message=Enter commit message: 

echo.
echo Committing changes...
git commit -m "%commit_message%"

echo.
echo Pushing to GitHub...
git push

echo.
echo Process completed!
echo Your changes should now be on GitHub.
pause