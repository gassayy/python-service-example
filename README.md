# Service Example

A FastAPI service example with PostgreSQL integration.

## Setup

1. Install Python 3.12+ from [python.org](https://python.org) or using your system's package manager:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12

# macOS with Homebrew
brew install python@3.12

# Windows
# Download installer from python.org and run it
```

2. Install and use uv:
```bash
# Install uv
pip install uv

# Install dependencies (uv automatically creates and uses a virtualenv)
uv pip sync
```

3. Create `.env` file:
```bash
cp app/.env.example app/.env
# Edit .env with your database credentials:
# DB_CONN_URL=postgresql://postgres:your_password@localhost:5432/service_example

# assume you will run the app from the root of the project
ln -s ./app/.env .env

4. Initialize database schema:
```bash
# Create tables
psql -U postgres -d service_example -f app/scripts/init.sql

# Generate and insert sample data
python -m app.scripts.gen_users
psql -U postgres -d service_example -f insert_data.sql
```

5. Run postgres and pgadmin from docker-compose

```
docker compose -f ./docker/docker-compose.yml up -d

# stop
docker compose -f ./docker/docker-compose.yml down

PGPASSWORD=<postgres_password> psql -h localhost -p 5432 -U postgres -c "CREATE DATABASE service_example;"
# 
PGPASSWORD=<postgres_password> psql -h localhost -p 5432 -U postgres -d service_example -f app/scripts/init.sql
# insert dummy data
PGPASSWORD=<postgres_password> psql -h localhost -p 5432 -U postgres -d service_example -f app/scripts/insert_data.sql
```

5. Run the service:
```bash
# Development mode with auto-reload
python -m app
```

5. Access the API:
- API documentation: http://localhost:8000/docs
- API endpoints:
  - GET /users - List all users
  - GET /users/{id} - Get user by ID
  - GET /users/usernames - Get list of usernames

## Development

- Set `DEBUG=true` in `.env` for development features:
  - Auto-reload on code changes
  - Detailed error messages
  - Debug level logging
