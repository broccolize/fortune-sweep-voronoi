@echo off
setlocal
pushd "%~dp0.."
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" tools\build_report.py %*
) else (
  py -3 tools\build_report.py %*
)
set "report_exit=%errorlevel%"
popd
exit /b %report_exit%
