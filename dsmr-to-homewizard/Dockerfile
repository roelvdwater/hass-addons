ARG BUILD_FROM
# or the most recent version of the base image
FROM ${BUILD_FROM}

# Copy the add-on metadata (config.json, etc.)
COPY run.sh server.py /

# Install any necessary system dependencies and Python packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-requests \
    py3-zeroconf

# Make the script executable
RUN chmod +x /server.py /run.sh

# Run the script when the add-on starts
CMD [ "/run.sh" ]