@echo off
echo Testing HackRx 6.0 API with Windows curl...

REM Test 1: Health check
echo.
echo Testing health check...
curl -X GET "http://127.0.0.1:8000/api/v1/health"

echo.
echo.
echo Testing main API endpoint...
echo.

REM Test 2: Main API with properly escaped JSON
curl -X POST "http://127.0.0.1:8000/api/v1/hackrx/run" ^
-H "Content-Type: application/json" ^
-H "Authorization: Bearer 273418978cb9f079f5da0cd221de3a8c4ae3d5a9b29477367d3e51c2f3763444" ^
-d "{\"documents\": \"https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03^&st=2025-07-04T09%%3A11%%3A24Z^&se=2027-07-05T09%%3A11%%00Z^&sr=b^&sp=r^&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%%2FjUHNO7HzQ%%3D\", \"questions\": [\"What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?\",\"Does this policy cover maternity expenses?\"]}"

echo.
echo Test completed.
pause
