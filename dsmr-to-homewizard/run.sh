#!/usr/bin/with-contenv bashio

# Read the configuration from /data/options.json
CONFIG_PATH=/data/options.json

bashio::log.info "Read values"

# Extract the hostname and access_code from the JSON file
LONG_LIVED_ACCESS_TOKEN=$(bashio::config 'long_lived_access_token')
HOME_ASSISTANT_URL=$(bashio::config 'home_assistant_url')
SERIAL=$(bashio::config 'serial')
DISABLE_SSL_CHECK=$(bashio::config 'disable_ssl_check')

# Call the Python script with the extracted configuration
python3 /server.py "$LONG_LIVED_ACCESS_TOKEN" "$HOME_ASSISTANT_URL" "$SERIAL" "$DISABLE_SSL_CHECK"