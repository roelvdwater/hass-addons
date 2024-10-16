#!/usr/bin/with-contenv bashio

# Read the configuration from /data/options.json
CONFIG_PATH=/data/options.json

bashio::log.info "Read values"

# Extract the hostname and access_code from the JSON file
HOSTNAME=$(bashio::config 'hostname')
ACCESS_CODE=$(bashio::config 'access_code')

# Call the Python script with the extracted configuration
python3 /webcam.py --hostname "$HOSTNAME" --password "$ACCESS_CODE"