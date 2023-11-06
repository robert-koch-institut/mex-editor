@echo off

set target=%1

if "%target%"=="install" goto install
if "%target%"=="test" goto test
echo invalid argument %target%
exit /b 1


:install
@REM install meta requirements system-wide
echo follow https://learn.microsoft.com/en-us/windows/dev-environment/javascript/nodejs-on-windows
exit /b 1

@REM run the npm installation
echo installing packages
npm install
exit /b %errorlevel%


:test
@REM run the linter hooks configured in package.json
echo linting all files
npm run lint
if %errorlevel% neq 0 exit /b %errorlevel%

@REM run the karma test suite with all tests
echo running all tests
npm run test
exit /b %errorlevel%
