Write-Host 'Starting Lyrivane Studio with Docker Compose...' -ForegroundColor Cyan
docker-compose up -d --build
Write-Host 'Studio is starting in the background! Wait a few seconds for services to initialize.' -ForegroundColor Green
Write-Host 'Frontend: http://localhost:3015'
Write-Host 'API: http://localhost:8005'
