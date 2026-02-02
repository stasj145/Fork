#!/bin/sh

# Create the images directory if it doesn't exist
mkdir -p /app/images

# Fix permissions: Change ownership of the volume mount to appuser
chown -R appuser:appuser /app/images

# Drop privileges and execute the command passed to docker
exec gosu appuser "$@"