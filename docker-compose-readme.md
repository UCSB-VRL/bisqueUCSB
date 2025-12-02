# BisQue Docker Compose Setup

This Docker Compose setup allows you to easily run BisQue with persistent data storage and intelligent build caching.

## Quick Start

```bash
# Copy environment template
cp .env.example .env

# Build and start (uses Docker cache intelligently)
docker compose up --build -d
```

## Daily Usage

```bash
# Normal startup
docker compose up -d

# Stop BisQue
docker compose down

# View logs
docker compose logs -f

# Restart without rebuilding
docker compose restart
```

## Complete cleanup and build
```bash
# stop container with cleaning persistent data
docker compose down -v
docker compose up --build -d
# or without using cache
docker compose build --no-cache && docker compose up -d
# to check the logs
docker compose logs -f