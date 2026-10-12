#!/bin/sh
set -eu

# Require the SSH password
if [ -z "${SSH_PASSWORD:-}" ]; then
    echo "ERROR: SSH_PASSWORD is required"
    exit 1
fi

# Configure the SSH account password
printf '%s:%s\n' "tmd-rfdmc" "$SSH_PASSWORD" | chpasswd

# Prepare the output directory
mkdir -p /output
chown -R tmd-rfdmc:tmd-rfdmc /output
chmod 750 /output

# Generate SSH host keys
ssh-keygen -A

# Start SSH in the background
/usr/sbin/sshd

# Verify cron exists before starting it
if command -v cron >/dev/null 2>&1; then
    echo "Starting cron scheduler..."
    exec /usr/sbin/cron -f
else
    echo "ERROR: cron is not installed."
    exit 1
fi