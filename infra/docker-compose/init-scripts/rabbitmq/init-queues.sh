#!/bin/bash
# RabbitMQ Queue Initialization Script
# Creates default queues for async task processing

set -e

echo "🐰 Waiting for RabbitMQ to be ready..."
sleep 10

echo "🔧 Creating RabbitMQ queues..."

# RabbitMQ Management API endpoint
RABBITMQ_HOST="${RABBITMQ_HOST:-localhost}"
RABBITMQ_PORT="${RABBITMQ_MGMT_PORT:-15672}"
RABBITMQ_USER="${RABBITMQ_DEFAULT_USER:-admin}"
RABBITMQ_PASS="${RABBITMQ_DEFAULT_PASS:-changeme}"
RABBITMQ_VHOST="${RABBITMQ_DEFAULT_VHOST:-/}"

# URL encode the vhost
VHOST_ENCODED=$(echo "$RABBITMQ_VHOST" | sed 's/\//%2F/g')

# Base URL for API calls
BASE_URL="http://${RABBITMQ_USER}:${RABBITMQ_PASS}@${RABBITMQ_HOST}:${RABBITMQ_PORT}/api"

# Function to create queue
create_queue() {
    local queue_name=$1
    local durable=${2:-true}
    local auto_delete=${3:-false}
    
    echo "Creating queue: $queue_name"
    curl -i -u "${RABBITMQ_USER}:${RABBITMQ_PASS}" \
         -X PUT \
         -H "content-type:application/json" \
         -d "{\"durable\":${durable},\"auto_delete\":${auto_delete}}" \
         "${BASE_URL}/queues/${VHOST_ENCODED}/${queue_name}"
}

# Function to create exchange
create_exchange() {
    local exchange_name=$1
    local exchange_type=${2:-direct}
    local durable=${3:-true}
    
    echo "Creating exchange: $exchange_name"
    curl -i -u "${RABBITMQ_USER}:${RABBITMQ_PASS}" \
         -X PUT \
         -H "content-type:application/json" \
         -d "{\"type\":\"${exchange_type}\",\"durable\":${durable}}" \
         "${BASE_URL}/exchanges/${VHOST_ENCODED}/${exchange_name}"
}

# Function to bind queue to exchange
bind_queue() {
    local queue_name=$1
    local exchange_name=$2
    local routing_key=$3
    
    echo "Binding queue $queue_name to exchange $exchange_name with routing key $routing_key"
    curl -i -u "${RABBITMQ_USER}:${RABBITMQ_PASS}" \
         -X POST \
         -H "content-type:application/json" \
         -d "{\"routing_key\":\"${routing_key}\"}" \
         "${BASE_URL}/bindings/${VHOST_ENCODED}/e/${exchange_name}/q/${queue_name}"
}

# Create exchanges
create_exchange "anki.tasks" "topic" true
create_exchange "anki.events" "topic" true
create_exchange "anki.dlx" "topic" true

# Create main task queues
create_queue "pdf.processing" true false
create_queue "deck.generation" true false
create_queue "embedding.generation" true false
create_queue "notifications" true false

# Create dead letter queues
create_queue "pdf.processing.dlq" true false
create_queue "deck.generation.dlq" true false
create_queue "embedding.generation.dlq" true false

# Bind queues to exchanges
bind_queue "pdf.processing" "anki.tasks" "pdf.process"
bind_queue "deck.generation" "anki.tasks" "deck.generate"
bind_queue "embedding.generation" "anki.tasks" "embedding.generate"
bind_queue "notifications" "anki.events" "notification.*"

# Bind dead letter queues
bind_queue "pdf.processing.dlq" "anki.dlx" "pdf.process"
bind_queue "deck.generation.dlq" "anki.dlx" "deck.generate"
bind_queue "embedding.generation.dlq" "anki.dlx" "embedding.generate"

echo "✅ RabbitMQ queues created successfully!"
echo "📊 Exchanges: anki.tasks, anki.events, anki.dlx"
echo "📦 Queues:"
echo "   - pdf.processing"
echo "   - deck.generation"
echo "   - embedding.generation"
echo "   - notifications"
echo "   - Dead letter queues (*.dlq)"
