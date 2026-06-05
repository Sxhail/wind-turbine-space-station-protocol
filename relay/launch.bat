@echo off
:: ============================================================
:: launch.bat — LEO Satellite Relay Node
:: Contributor: Yash Chhillar
:: CSU33D03 Group 3
::
:: BEFORE RUNNING: Open config.py and replace
:: <<SUHAIL_IP>> with Suhail's IP
:: <<KANISHK_IP>> with Kanishk's IP
::
:: START THIS FIRST before the turbine and station.
:: ============================================================

echo =============================================
echo  Group 3 — Satellite Relay Node
echo  Starting relay...
echo =============================================
echo.

start "Satellite Relay" cmd /k "python relay.py"

echo.
echo Relay launched. Start turbine next, then station.
echo Close this window when done.
pause
