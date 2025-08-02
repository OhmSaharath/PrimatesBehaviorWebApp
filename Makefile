# Makefile for managing Docker services and common tasks
# .PHONY ensures these commands run even if a file with the same name exists.
# OS-specific commands for cross-platform compatibility
# OS-specific commands and paths for cross-platform compatibility
ifeq ($(OS),Windows_NT)
	COPY = copy
	WAIT = powershell -Command "Start-Sleep -Seconds 15"
	# Windows uses backslashes for host paths
	URLS_INITIAL = config\urls_initial.py
	URLS_FINAL = config\urls_final.py
	URLS_DEST = PrimatesGame\urls.py
else
	COPY = cp
	WAIT = sleep 15
	# Linux/macOS use forward slashes for host paths
	URLS_INITIAL = config/urls_initial.py
	URLS_FINAL = config/urls_final.py
	URLS_DEST = PrimatesGame/urls.py
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

# Command for the very first project setup
.PHONY: first-setup

first-setup:
	@echo "--- 1. Building all images ---"
	@docker-compose build

	@echo "\n--- 2. Starting database and redis services ---"
	@docker-compose up -d db redis

	@echo "\n--- 3. Waiting for database to initialize (15 seconds) ---"
	@$(WAIT)

	@echo "\n--- 4. Setting up initial URLs and deleting old migration ---"
	@$(COPY) $(URLS_INITIAL) $(URLS_DEST)
	@docker-compose run --rm app rm -f PrimatesGameAPI/migrations/0001_initial.py

	@echo "\n--- 5. Running initial migrations ---"
	@docker-compose run --rm app python manage.py makemigrations
	@docker-compose run --rm app python manage.py migrate

	@echo "\n--- 6. Creating initial Superuser and Groups ---"
	@docker-compose run --rm app python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', '', '@dmin1234')"
	@docker-compose run --rm app python manage.py shell -c "from django.contrib.auth.models import Group; Group.objects.get_or_create(name='Researcher'); Group.objects.get_or_create(name='RPiClient')"

	@echo "\n--- 7. Activating final URLs ---"
	@$(COPY) $(URLS_FINAL) $(URLS_DEST)

	@echo "\n--- ✅ First-time setup complete! Shutting down to apply all changes.---"
	@docker-compose down

	@echo "\n--- ✨ You can now start your project with 'make up' ---"