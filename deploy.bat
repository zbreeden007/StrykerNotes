@echo off
setlocal enabledelayedexpansion

:: Define your branch name
set BRANCH_NAME=main

:: Display information and confirm
echo Preparing to deploy to branch: %BRANCH_NAME%
echo Working directory: %cd%
set /p confirm=Continue with deployment? (y/n): 

if not "%confirm%"=="y" (
  echo Deployment cancelled.
  exit /b 1
)

:: Stage all changes
echo Staging changes...
git add .

:: Get commit message from user
set /p commit_message=Enter commit message: 

:: Commit changes
echo Committing changes...
git commit -m "%commit_message%"

:: Show current branch
echo Current branch:
git branch

:: Show remote configuration
echo Remote configuration:
git remote -v

:: Push to remote
echo Pushing to remote repository...
git push origin %BRANCH_NAME%

echo Deployment completed successfully!
pause