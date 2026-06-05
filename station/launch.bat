@echo off
:: ============================================================
:: launch.bat — Space Station Node
:: Contributor: Kanishk Daga
:: CSU33D03 Group 3
::
:: BEFORE RUNNING: Open command_sender.py and replace
:: <<YASH_IP>> with Yash's actual IP address.
::
:: START THIS LAST after relay and turbine are running.
::
:: Windows 1: sensor_receiver.py   (receives turbine data)
:: Window 2:  heartbeat_monitor.py (detects blackouts)
:: Window 3:  command_sender.py    (type PITCH:30 or YAW:45)
:: ============================================================

echo =============================================
echo  Group 3 — Space Station Node
echo  Starting 3 processes...
echo =============================================
echo.

start "Sensor Receiver - Port 5003" cmd /k "python sensor_receiver.py"
timeout /t 1 /nobreak >nul

start "Heartbeat Monitor - Port 5004" cmd /k "python heartbeat_monitor.py"
timeout /t 1 /nobreak >nul

start "Command Sender (DEMO)" cmd /k "python command_sender.py"

echo.
echo All 3 station processes launched.
echo Type PITCH:30 or YAW:45 in the Command Sender window.
echo Close this window when done.
pause
