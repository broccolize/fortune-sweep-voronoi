@echo off
setlocal
set "report_root=%~dp0.."
if not exist "%report_root%\tools\build_report.py" set "report_root=%~dp0..\02_SourceCode"
if exist "%report_root%\.venv\Scripts\python.exe" (
  "%report_root%\.venv\Scripts\python.exe" "%~dp0build_snapshot.py" %*
) else (
  py -3 "%~dp0build_snapshot.py" %*
)
exit /b %errorlevel%
