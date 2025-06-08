FROM python:3.13-slim

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

# Expose SSH and Flask ports
EXPOSE 22 5000

RUN mkdir -p /run/sshd && ssh-keygen -A

# Start the SSH server to allow connections
CMD ["/usr/sbin/sshd", "-D"] 