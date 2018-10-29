#!/usr/bin/env bash

# Fetch the google cloud SDK, note that the version may need to be updated!
wget "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-222.0.0-linux-x86_64.tar.gz"

# Extract and cleanup the tar file
tar -xvzf google-cloud-sdk-222.0.0-linux-x86_64.tar.gz
rm google-cloud-sdk-222.0.0-linux-x86_64.tar.gz

# Install the SDK
install.sh

# Clean up the directory
rm -rf google-cloud-sdk-222.0.0-linux-x86_64

echo "Note: You will need to restart the browser at this point for the bashrc pathing to take effect."
echo "After that run:"
echo ">>> gcloud init"