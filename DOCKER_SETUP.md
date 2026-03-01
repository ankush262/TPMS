# Docker Compose Quick Start Guide

## Prerequisites
- Docker Desktop installed and running
- Docker Compose (comes with Docker Desktop)
- Git

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TPMS
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the services**
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Frontend: http://localhost:3000
   - Analytics/Jupyter: http://localhost:8888
   - Database: localhost:5432

## Useful Commands

### View logs
```bash
docker-compose logs -f backend          # Follow backend logs
docker-compose logs -f frontend         # Follow frontend logs
docker-compose logs -f db               # Follow database logs
docker-compose logs                     # All logs
```

### Restart services
```bash
docker-compose restart                  # Restart all services
docker-compose restart backend          # Restart specific service
```

### Stop services
```bash
docker-compose down                     # Stop and remove containers
docker-compose down -v                  # Also remove volumes (WARNING: deletes data)
```

### Build without starting
```bash
docker-compose build
```

### Execute commands in running container
```bash
docker-compose exec backend bash        # Access backend shell
docker-compose exec frontend sh         # Access frontend shell
docker-compose exec db psql -U tpms_user -d tpms_db  # Connect to database
```

### View running containers
```bash
docker-compose ps
```

## Services Overview

### Backend (FastAPI)
- **Port**: 8000
- **Auto-reload**: Enabled during development
- **Health check**: GET /health
- **API Docs**: /docs (Swagger UI), /redoc (ReDoc)

### Frontend (React)
- **Port**: 3000
- **Hot reload**: Enabled during development
- **API URL**: Connected to backend at http://backend:8000

### Database (PostgreSQL)
- **Port**: 5432
- **Username**: tpms_user
- **Password**: tpms_password
- **Database**: tpms_db
- **Data**: Persisted in `postgres_data` volume

### Analytics (Jupyter Notebook)
- **Port**: 8888
- **Access**: Open http://localhost:8888 in browser
- **Data**: Access to all project files

## Troubleshooting

### Services won't start
```bash
docker-compose down
docker-compose up --build
```

### Port already in use
Change the port mapping in docker-compose.yml or docker-compose.override.yml

### Database connection errors
```bash
docker-compose restart db
docker-compose restart backend
```

### Clear everything and start fresh
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

## Development Workflow

1. **Make code changes** - Changes are reflected immediately due to volume mounts
2. **Backend changes** - Auto-reload enabled (uvicorn --reload)
3. **Frontend changes** - Hot reload enabled (React)
4. **Database schema changes** - May need to restart backend
5. **New dependencies** - Rebuild: `docker-compose build && docker-compose up -d`

## Production Notes
For production deployment:
- Remove `--reload` flag from backend
- Set `NODE_ENV=production` for frontend
- Use environment variables for sensitive credentials
- Set up proper database backups
- Use proper SSL/TLS certificates
- Scale services as needed with additional containers
