# Start stack (dev mode with hot reload)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Start in background
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Stop stack
docker compose down

# Restart a single service
docker compose restart backend
docker compose restart postgres

# Rebuild backend image (after dependency changes)
docker compose up --build backend

# View logs
docker compose logs backend --tail=20
docker compose logs backend --tail=50
docker compose logs -f backend          # follow/stream

# Run a command inside a container
docker compose exec backend <command>
docker compose exec postgres <command>