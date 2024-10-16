ARG BUILD_FROM
# or the most recent version of the base image
FROM ${BUILD_FROM}

# Copy the add-on metadata (config.json, etc.)
COPY run.sh /

# Install any necessary system dependencies and Python packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-pillow

# Make the script executable
RUN chmod a+x /run.sh

# Run the script when the add-on starts
CMD [ "/run.sh" ]