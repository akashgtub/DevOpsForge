@echo off
setlocal EnableExtensions
title DevOpsForge - Start All Services

set "ROOT=%~dp0"
set "JENKINS_NAME=devopsforge-jenkins"
set "JENKINS_IMAGE=jenkins/jenkins:lts-jdk17"

echo.
echo ==========================================
echo        DEVOPSFORGE STARTUP MANAGER
echo ==========================================
echo Project: %ROOT%
echo.

echo [1/6] Checking Docker Desktop...
docker info >nul 2>&1
if errorlevel 1 (
    echo Docker Engine is not ready. Starting Docker Desktop...
    if exist "%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe" (
        start "" "%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe"
    ) else (
        echo ERROR: Docker Desktop executable was not found.
        echo Start Docker Desktop manually, then run this file again.
        pause
        exit /b 1
    )
)

set /a COUNT=0
:WAIT_DOCKER
docker info >nul 2>&1
if not errorlevel 1 goto DOCKER_READY
set /a COUNT+=1
if %COUNT% GEQ 60 (
    echo ERROR: Docker Engine did not become ready within 120 seconds.
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul
goto WAIT_DOCKER

:DOCKER_READY
echo Docker Engine is ready.
echo.

echo [2/6] Starting FastAPI and PostgreSQL with Docker Compose...
pushd "%ROOT%"
if not exist "docker-compose.yml" (
    echo ERROR: docker-compose.yml was not found in %ROOT%
    popd
    pause
    exit /b 1
)
docker compose up --build -d
if errorlevel 1 (
    echo.
    echo ERROR: Docker Compose could not start.
    echo If devopsforge-postgres name is already in use, run ONCE:
    echo   docker rm -f devopsforge-postgres
    echo Do NOT remove the database volume.
    popd
    pause
    exit /b 1
)
popd
echo.

echo [3/6] Starting Jenkins...
docker inspect "%JENKINS_NAME%" >nul 2>&1
if not errorlevel 1 (
    docker start "%JENKINS_NAME%" >nul
    if errorlevel 1 echo WARNING: Jenkins container could not be started.
) else (
    echo Creating Jenkins container for the first time...
    docker run -d --name "%JENKINS_NAME%" -p 8081:8080 -p 50000:50000 -v devopsforge_jenkins_home:/var/jenkins_home "%JENKINS_IMAGE%"
    if errorlevel 1 echo WARNING: Jenkins could not be created.
)
echo.

echo [4/6] Checking local Kubernetes...
where kubectl >nul 2>&1
if errorlevel 1 (
    echo WARNING: kubectl is not installed or not on PATH.
) else (
    kubectl config current-context
    if errorlevel 1 (
        echo WARNING: No Kubernetes context. Enable Kubernetes in Docker Desktop.
    ) else (
        kubectl get nodes
        if errorlevel 1 echo WARNING: Kubernetes cluster is not ready. Check Docker Desktop settings.
    )
)
echo.

echo [5/6] Checking Terraform...
where terraform >nul 2>&1
if errorlevel 1 (
    echo WARNING: Terraform is not installed or not on PATH.
) else (
    terraform --version
)
echo NOTE: No terraform apply is run; this script creates no cloud infrastructure.
echo.

echo [6/6] Service status...
pushd "%ROOT%"
docker compose ps
popd
echo.
echo API:     http://localhost:8000/docs
echo Health:  http://localhost:8000/health
echo Jenkins: http://localhost:8081
echo.
echo Jenkins first-time password:
echo docker exec %JENKINS_NAME% cat /var/jenkins_home/secrets/initialAdminPassword
echo.
echo Kubernetes is checked but workloads are not deployed by this script yet.
echo Review WARNING messages above.
pause
endlocal
