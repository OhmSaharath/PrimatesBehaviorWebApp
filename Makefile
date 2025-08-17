# Makefile for managing Docker services and common tasks
# .PHONY ensures these commands run even if a file with the same name exists.
# OS-specific commands for cross-platform compatibility
# OS-specific commands and paths for cross-platform compatibility
include .env
export MYSQL_ROOT_PASSWORD
DB_SERVICE = db
DB_NAME = PrimatesGameDB

ifeq ($(OS),Windows_NT)
	COPY = copy
	WAIT = powershell -Command "Start-Sleep -Seconds 15"
	# Windows uses backslashes for host paths
	BACKUP_PATH = .\backup
	BACKUP_FILE = $(BACKUP_PATH)\PrimatesGameDB.sql
else
	COPY = cp
	WAIT = sleep 15
	# Linux/macOS use forward slashes for host paths
	BACKUP_PATH = ./backup
	BACKUP_FILE = $(BACKUP_PATH)/PrimatesGameDB.sql
endif

.PHONY: build up down stop logs shell migrate collectstatic

# Build or rebuild the docker images
build:
	@echo "Building Docker images..."
	@docker-compose build

# Start all services in detached mode
up:
	@echo "Starting services in detached mode..."
	@docker-compose up -d

# Stop and remove all services
down:
	@echo "Stopping and removing services..."
	@docker-compose down

# Stop services without removing them
stop:
	@echo "Stopping services..."
	@docker-compose stop

# View logs from all services (use 'make logs app' for just the app)
logs:
	@echo "Tailing logs..."
	@docker-compose logs -f

# Access the shell of the app container
shell:
	@echo "Accessing app container shell..."
	@docker-compose exec app /bin/bash

# Example: Run Django migrations inside the app container
migrate:
	@echo "Running Django migrations..."
	@docker-compose exec app python manage.py migrate

collectstatic:
	@echo "Collecting static files into STATIC_ROOT..."
	@docker-compose exec app python manage.py collectstatic --noinput --clear

# Command for setup project
.PHONY: setup

setup:
	@echo "--- 1. Building all images ---"
	@docker-compose build

	@echo "\n--- 2. Starting database and redis services ---"
	@docker-compose up -d db redis

	@echo "\n--- 3. Waiting for database to initialize (15 seconds) ---"
	@$(WAIT)

	@echo "\n--- 4. Database restored from $(BACKUP_FILE)---"
	@docker-compose exec -T -e MYSQL_PWD=$(MYSQL_ROOT_PASSWORD) $(DB_SERVICE) mysql -u root -e "DROP DATABASE IF EXISTS $(DB_NAME);"
	@docker-compose exec -T -e MYSQL_PWD=$(MYSQL_ROOT_PASSWORD) $(DB_SERVICE) mysql -u root -e "CREATE DATABASE $(DB_NAME);"
	@docker-compose exec -T -e MYSQL_PWD=$(MYSQL_ROOT_PASSWORD) $(DB_SERVICE) mysql -u root $(DB_NAME) < $(BACKUP_FILE)
	
	@echo "\n--- Test setup complete! Shutting down to apply all changes.---"
	@docker-compose down

	@echo "\n--- ✨ You can now start your project with 'make up' ---"