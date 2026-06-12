@echo off
chcp 65001 > nul
setlocal

set IDEA_MVN=C:\Program Files\JetBrains\IntelliJ IDEA Community Edition 2025.2.6.2\plugins\maven\lib\maven3\bin\mvn.cmd
set ROOT=%~dp0

if not exist "%IDEA_MVN%" (
    echo [오류] IntelliJ Maven not found: %IDEA_MVN%
    pause
    exit /b 1
)

echo [Backend]  Spring Boot ^(localhost:8080^) 시작...
start "Backend" cmd /k "cd /d "%ROOT%book-server" && "%IDEA_MVN%" spring-boot:run"

timeout /t 5 /nobreak > nul

echo [Frontend] React ^(localhost:5173^) 시작...
start "Frontend" cmd /k "cd /d "%ROOT%book-manager" && npm run dev"

echo.
echo Backend  : http://localhost:8080
echo Frontend : http://localhost:5173
echo H2 Console: http://localhost:8080/h2-console
echo.
echo 각 창에서 Ctrl+C 로 종료하세요.
endlocal
