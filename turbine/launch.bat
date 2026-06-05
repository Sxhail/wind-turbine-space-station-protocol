@echo off
:: ============================================================
:: launch.bat — Wind Turbine Node
:: Contributor: Suhail Jameel
:: CSU33D03 Group 3
::
:: BEFORE RUNNING: Open protocol.py, pitch_listener.py,
:: yaw_listener.py, sensor_sender.py and heartbeat.py
:: and replace <<YASH_IP>> with Yash's actual IP address.
::
:: This script opens 4 terminal windows, one for each process.
:: ============================================================

echo =============================================
echo  Group 3 — Wind Turbine Node
echo  Starting 4 processes...
echo =============================================
echo.

start "Pitch Listener - Port 5001" cmd /k "python pitch_listener.py"
timeout /t 1 /nobreak >nul

start "Yaw Listener - Port 5002" cmd /k "python yaw_listener.py"
timeout /t 1 /nobreak >nul

start "Sensor Sender - Port 5003" cmd /k "python sensor_sender.py"
timeout /t 1 /nobreak >nul

start "Heartbeat - Port 5004" cmd /k "python heartbeat.py"

echo.
echo All 4 turbine processes launched.
echo Close this window when done.
pause
