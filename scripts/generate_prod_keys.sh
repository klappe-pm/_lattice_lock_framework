#!/bin/bash
set -e

# Generate secure random keys
echo "Generating production secrets..."

SECRET_KEY=$(openssl rand -base64 48)
DB_PASSWORD=$(openssl rand -base64 24)
ADMIN_PASSWORD=$(openssl rand -base64 16)

# Create .env file for production
cat > .env.production << EOF
# Lattice Lock Production Environment
LATTICE_ENV=production
LATTICE_LOCK_SECRET_KEY=${SECRET_KEY}
DB_PASSWORD=${DB_PASSWORD}

# Logging
LOG_LEVEL=info

# Admin Initial Setup (Change after first login)
ADMIN_INITIAL_PASSWORD=${ADMIN_PASSWORD}
EOF

echo "Secrets generated in .env.production"
echo "Secure this file! Do not commit it to version control."
