#!/bin/sh
# MinIO Bucket Initialization Script
# Creates default buckets for PDFs and Anki decks
# This script is run by the minio-init service in docker-compose

set -e

echo "🗄️  Initializing MinIO buckets..."

# Wait for MinIO to be fully ready
sleep 5

# MinIO connection details from environment
MINIO_HOST="${MINIO_HOST:-minio:9000}"
MINIO_USER="${MINIO_ROOT_USER:-minioadmin}"
MINIO_PASS="${MINIO_ROOT_PASSWORD:-changeme123}"
MINIO_ALIAS="myminio"

# Configure MinIO client
echo "Configuring MinIO client..."
mc alias set ${MINIO_ALIAS} http://${MINIO_HOST} ${MINIO_USER} ${MINIO_PASS}

# Create buckets
echo "Creating bucket: pdfs"
mc mb --ignore-existing ${MINIO_ALIAS}/pdfs

echo "Creating bucket: decks"
mc mb --ignore-existing ${MINIO_ALIAS}/decks

echo "Creating bucket: temp"
mc mb --ignore-existing ${MINIO_ALIAS}/temp

# Set bucket policies (allow public read for generated decks)
echo "Setting bucket policies..."
mc anonymous set download ${MINIO_ALIAS}/decks

# Optional: Set lifecycle policies for temp bucket (auto-delete after 7 days)
cat > /tmp/lifecycle.json <<EOF
{
    "Rules": [
        {
            "ID": "temp-cleanup",
            "Status": "Enabled",
            "Expiration": {
                "Days": 7
            }
        }
    ]
}
EOF

echo "Setting lifecycle policy for temp bucket..."
mc ilm import ${MINIO_ALIAS}/temp < /tmp/lifecycle.json

# Create subdirectories/prefixes (optional, for organization)
echo "Creating directory structure..."
mc cp --recursive /dev/null ${MINIO_ALIAS}/pdfs/uploads/ 2>/dev/null || true
mc cp --recursive /dev/null ${MINIO_ALIAS}/decks/generated/ 2>/dev/null || true

# Set versioning (optional)
echo "Enabling versioning..."
mc version enable ${MINIO_ALIAS}/pdfs
mc version enable ${MINIO_ALIAS}/decks

# Display bucket information
echo "✅ MinIO initialization complete!"
echo ""
echo "📊 Buckets created:"
mc ls ${MINIO_ALIAS}

echo ""
echo "📦 Bucket details:"
mc du ${MINIO_ALIAS}/pdfs
mc du ${MINIO_ALIAS}/decks
mc du ${MINIO_ALIAS}/temp

echo ""
echo "🔒 Bucket policies:"
mc anonymous get ${MINIO_ALIAS}/pdfs
mc anonymous get ${MINIO_ALIAS}/decks
mc anonymous get ${MINIO_ALIAS}/temp

echo ""
echo "✅ MinIO is ready to use!"
echo "   - Console UI: http://localhost:9001"
echo "   - API Endpoint: http://localhost:9000"
echo "   - Buckets: pdfs, decks, temp"
