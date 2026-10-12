FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    openssh-server \
    cron \
    tzdata \
    passwd \
    util-linux \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

# Create the application and SSH user    
RUN useradd --create-home --shell /bin/bash \
     --uid 10001 tmd-rfdmc \
    && mkdir -p /run/sshd /output \
    && chown -R tmd-rfdmc:tmd-rfdmc /output


RUN printf '%s\n' \
    'PermitRootLogin no' \
    'PasswordAuthentication yes' \
    'KbdInteractiveAuthentication no' \
    'PubkeyAuthentication no' \
    'AllowUsers tmd-rfdmc' \
    'PermitEmptyPasswords no' \
    > /etc/ssh/sshd_config.d/99-tmd-rfdmc.conf

RUN apt-get update && apt-get install -y iproute2 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code and data
COPY --chown=tmd-rfdmc:tmd-rfdmc app/ /app/
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY tmd-rfdmc.cron /etc/cron.d/tmd-rfdmc

RUN chmod 755 /usr/local/bin/docker-entrypoint.sh \
    && chmod 644 /etc/cron.d/tmd-rfdmc

# Keep Python output visible in Docker logs
ENV PYTHONUNBUFFERED=1
ENV OUTPUT_DIR=/output

EXPOSE 22

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]