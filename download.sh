#!/bin/bash

# Configuration
S3_BUCKET_URL="https://downloads.zinc.dev/releases/openobserve"  # Replace with your actual S3 bucket URL

# Detect platform
echo "Detecting platform..."
case "$(uname -s)" in
    Linux*)     PLATFORM="linux";;
    Darwin*)    PLATFORM="darwin";;
    CYGWIN*|MINGW32*|MSYS*|MINGW*) PLATFORM="windows";;
    *)          PLATFORM="unknown";;
esac

if [ "$PLATFORM" = "unknown" ]; then
    echo "Error: Unsupported platform."
    exit 1
fi

echo "Platform detected: $PLATFORM"

# Detect architecture
echo "Detecting architecture..."
ARCH=$(uname -m)

case "$ARCH" in
    x86_64) ARCH="amd64";;
    arm64)  ARCH="arm64";;
    aarch64) ARCH="arm64";;
    *)      ARCH="unknown";;
esac

if [ "$ARCH" = "unknown" ]; then
    echo "Error: Unsupported architecture."
    exit 1
fi

echo "Architecture detected: $ARCH"

# Optional: Specify version (default: latest)
VERSION=${1:-latest}

# Construct file name
# if [ "$VERSION" = "latest" ]; then
#     FILE_NAME="openobserve-${PLATFORM}-${ARCH}.tar.gz"
# else
#     FILE_NAME="openobserve-${VERSION}-${PLATFORM}-${ARCH}.tar.gz"
# fi
FILE_NAME="openobserve-${VERSION}-${PLATFORM}-${ARCH}.tar.gz"

DOWNLOAD_URL="${S3_BUCKET_URL}/${VERSION}/${FILE_NAME}"

echo "Downloading from S3: $DOWNLOAD_URL"
curl -fLo latest_release.tar.gz "$DOWNLOAD_URL"

# Verify download
if [ $? -ne 0 ]; then
    echo "Error: Download failed. Make sure the file exists in S3."
    exit 1
fi

# Extract the downloaded asset
echo "Extracting the downloaded file..."
tar -xzf latest_release.tar.gz

# Cleanup
rm latest_release.tar.gz

echo "Download and extraction complete!"