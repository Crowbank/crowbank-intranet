Project Brief: Dockerized Development Environment for Crowbank Intranet
Last Updated: 8 June 2025

1. Project Goal
The primary objective is to create a reliable, reproducible, and high-performance containerized development environment for a complex Flask application. This environment must run locally on a development machine (and eventually a Synology NAS), providing a "local codespace" experience that is superior to and more stable than cloud-based IDEs connected via network tunnels. The final architecture should facilitate a straightforward future deployment to a cloud production environment.

2. Core Architecture
The environment will be managed by Docker Compose. It will consist of multiple, interconnected services running in separate containers on a shared virtual network. This isolates dependencies and mirrors a modern production setup.

The required services are:

app: A dedicated development container with Python, Node.js, and an SSH server to allow direct connection from a local editor like Cursor. This is where all development work (running the Flask server, frontend builds) will happen.
database: The main PostgreSQL database for the application.
mcp_server: A middleware application that acts as a client to the database service.
pgadmin: A web-based GUI for managing the PostgreSQL databases.
3. Service Definitions & Requirements
app (The Development Container):

Purpose: To provide a consistent Linux environment for coding and running the Flask app.
Base: Must be built from a Dockerfile based on a standard Python image (e.g., python:3.11-slim).
Required Software: git, sudo, openssh-server, postgresql-client (for psql), nodejs & npm.
Connection: Must expose an SSH server on a mapped port (e.g., 2222) to allow connection via the "Remote - SSH" feature in Cursor.
Code Mounting: Must mount the local project source code directory into the container for live-editing.
database (Main PostgreSQL DB):

Image: postgres:16.9-alpine
Container Name: postgres-dev
Data Persistence: Must use a bind mount to the existing data directory located at /volume1/Dropbox/crowbank-intranet/postgres to preserve all current data.
Credentials: Must be configured via environment variables.
mcp_server (Middleware):

Image: mcp/postgres:latest
Container Name: mcp-postgres
Function: Acts as a client to the database service.
Configuration: Must be configured via environment variables, specifically a POSTGRES_URL that points to the database service (e.g., postgresql://user:pass@database:5432/dbname). Also requires NODE_VERSION, YARN_VERSION, and NODE_ENV.
pgadmin (Database GUI):

Image: dpage/pgadmin4:latest
Container Name: crowbank-pgadmin
Access: Must expose a port (e.g., 8080) to be accessible from the host's web browser.
Data Persistence: Must use a named volume to store server connection settings.
Credentials: Login credentials for the web UI must be configured via environment variables.
4. Key Configuration Files
These are the final, corrected blueprints for the entire stack.

File 1: docker-compose.yml

YAML

version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: crowbank-app-dev
    restart: unless-stopped
    ports:
      - "2222:22"    # For SSH connection from local Cursor
      - "5000:5000"  # For the Flask development server
    volumes:
      # Mount your project source code here
      - ./src:/app/src # Example: assuming your code is in a local 'src' folder
    networks:
      - dev-net

  database:
    image: postgres:16.9-alpine
    container_name: postgres-dev
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - /volume1/Dropbox/crowbank-intranet/postgres:/var/lib/postgresql/data
    networks:
      - dev-net

  mcp_server:
    image: mcp/postgres:latest
    container_name: mcp-postgres
    restart: unless-stopped
    depends_on:
      - database
    networks:
      - dev-net
    environment:
      NODE_VERSION: "22.16.0"
      YARN_VERSION: "1.22.22"
      NODE_ENV: "production"
      POSTGRES_URL: "postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}"

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: crowbank-pgadmin
    restart: unless-stopped
    environment:
      PGADMIN_DEFAULT_EMAIL: ${PGADMIN_DEFAULT_EMAIL}
      PGADMIN_DEFAULT_PASSWORD: ${PGADMIN_DEFAULT_PASSWORD}
    ports:
      - "8080:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - database
      - mcp_server
    networks:
      - dev-net

volumes:
  pgadmin_data:

networks:
  dev-net:
    name: dev-network
File 2: Dockerfile (for the app service)

Dockerfile

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

# Install system dependencies including SSH, git, node, and postgres client
RUN apt-get update && apt-get install -y \
    git sudo openssh-server postgresql-client curl \
    && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Create a non-root developer user with sudo access
RUN useradd -m -s /bin/bash devuser && \
    usermod -aG sudo devuser && \
    echo "devuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Configure SSH access (password-based for simple local dev)
RUN echo 'devuser:your-secure-ssh-password' | chpasswd && \
    mkdir -p /home/devuser/.ssh && \
    chown -R devuser:devuser /home/devuser/.ssh

# Set working directory
WORKDIR /app

# Expose the SSH port
EXPOSE 22

# Start the SSH server to allow connections
CMD ["/usr/sbin/sshd", "-D"]
File 3: .env (Template for Secrets)

Code snippet

# Main PostgreSQL Credentials
POSTGRES_USER=crowbank
POSTGRES_PASSWORD=ZhV8Pk521j1Z
POSTGRES_DB=crowbank

# pgAdmin Login Details
PGADMIN_DEFAULT_EMAIL=admin@yourdomain.com
PGADMIN_DEFAULT_PASSWORD=a-very-secure-pgadmin-password
5. Development Workflow
Setup: Place the docker-compose.yml, Dockerfile, and .env files in the root directory of the project on the local development machine.
Launch: Open a terminal in the project directory and run docker-compose up --build -d.
Connect Editor: Configure the "Remote - SSH" extension in Cursor to connect to localhost on port 2222 with the user devuser.
Develop: Once connected, the developer will be inside the app container. They can open a terminal to run flask, pip, npm, and psql commands directly against the other running containers.
6. Production Deployment Strategy
This architecture is designed for a smooth transition to the cloud:

Containerize the App: The Dockerfile for the app service creates a portable image of the application. For production, this image can be pushed to a container registry (like Docker Hub or AWS ECR).
Move to Managed Services: The database service will be replaced by a managed cloud database (like Neon or AWS RDS).
Update Configuration: The only required change for deployment is to update the environment variables (e.g., the DATABASE_URL) to point to the new cloud database. The application code itself does not need to change.
7. Summary of Key Decisions & Learnings
The project initially explored using GitHub Codespaces connected to an on-premise database via a Cloudflare Tunnel. This approach was abandoned after extensive troubleshooting revealed it to be complex and fragile, likely due to networking restrictions or subtle incompatibilities. The decision was made to pivot to a fully self-hosted Docker Compose environment. This provides a faster, more reliable, and simpler development workflow by keeping all services on a local network, while still following modern containerization practices that enable a clear path to future cloud deployment.