#!/bin/bash
# Smoke Test Script for Anki Compendium Docker Compose Environment
# Tests all services for availability and correct configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}⚠️  No .env file found, using defaults${NC}"
fi

# Default values
POSTGRES_USER=${POSTGRES_USER:-ankiuser}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-changeme}
POSTGRES_DB=${POSTGRES_DB:-anki_compendium_dev}
RABBITMQ_DEFAULT_USER=${RABBITMQ_DEFAULT_USER:-admin}
RABBITMQ_DEFAULT_PASS=${RABBITMQ_DEFAULT_PASS:-changeme}
MINIO_ROOT_USER=${MINIO_ROOT_USER:-minioadmin}
MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-changeme123}

# Helper functions
print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

test_start() {
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -n "  Testing: $1 ... "
}

test_pass() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    echo -e "${GREEN}✓ PASS${NC}"
}

test_fail() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo -e "${RED}✗ FAIL${NC}"
    if [ ! -z "$1" ]; then
        echo -e "    ${RED}Error: $1${NC}"
    fi
}

# Check if Docker Compose is running
check_docker_compose() {
    print_header "🐳 Docker Compose Status"
    
    test_start "Docker Compose services running"
    if docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
        test_pass
    else
        test_fail "Services not running. Run: docker-compose -f docker-compose.dev.yml up -d"
        exit 1
    fi
}

# Test PostgreSQL
test_postgresql() {
    print_header "🐘 PostgreSQL Tests"
    
    test_start "PostgreSQL is accessible"
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1;" > /dev/null 2>&1; then
        test_pass
    else
        test_fail "Cannot connect to PostgreSQL"
        return 1
    fi
    
    test_start "pgvector extension installed"
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM pg_extension WHERE extname = 'vector';" | grep -q "vector"; then
        test_pass
    else
        test_fail "pgvector extension not found"
    fi
    
    test_start "uuid-ossp extension installed"
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT * FROM pg_extension WHERE extname = 'uuid-ossp';" | grep -q "uuid-ossp"; then
        test_pass
    else
        test_fail "uuid-ossp extension not found"
    fi
    
    test_start "Initial tables created"
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB -c "\dt" | grep -q "users"; then
        test_pass
    else
        test_fail "Initial schema not created"
    fi
    
    test_start "Keycloak database exists"
    if PGPASSWORD=$POSTGRES_PASSWORD psql -h localhost -U $POSTGRES_USER -d keycloak -c "SELECT 1;" > /dev/null 2>&1; then
        test_pass
    else
        test_fail "Keycloak database not found"
    fi
}

# Test RabbitMQ
test_rabbitmq() {
    print_header "🐰 RabbitMQ Tests"
    
    test_start "RabbitMQ Management API accessible"
    if curl -s -u $RABBITMQ_DEFAULT_USER:$RABBITMQ_DEFAULT_PASS http://localhost:15672/api/overview > /dev/null; then
        test_pass
    else
        test_fail "Cannot access RabbitMQ Management API"
        return 1
    fi
    
    test_start "Default queues exist"
    if curl -s -u $RABBITMQ_DEFAULT_USER:$RABBITMQ_DEFAULT_PASS http://localhost:15672/api/queues | grep -q "pdf.processing"; then
        test_pass
    else
        test_fail "Default queues not created"
    fi
    
    test_start "Exchanges configured"
    if curl -s -u $RABBITMQ_DEFAULT_USER:$RABBITMQ_DEFAULT_PASS http://localhost:15672/api/exchanges | grep -q "anki.tasks"; then
        test_pass
    else
        test_fail "Exchanges not configured"
    fi
}

# Test MinIO
test_minio() {
    print_header "🗄️  MinIO Tests"
    
    test_start "MinIO API accessible"
    if curl -s http://localhost:9000/minio/health/live > /dev/null; then
        test_pass
    else
        test_fail "MinIO API not accessible"
        return 1
    fi
    
    test_start "MinIO Console accessible"
    if curl -s http://localhost:9001 > /dev/null; then
        test_pass
    else
        test_fail "MinIO Console not accessible"
    fi
    
    # Test bucket creation (requires mc client)
    if command -v mc &> /dev/null; then
        test_start "MinIO buckets created"
        mc alias set smoketest http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD > /dev/null 2>&1
        if mc ls smoketest | grep -q "pdfs"; then
            test_pass
        else
            test_fail "Default buckets not created"
        fi
        mc alias remove smoketest > /dev/null 2>&1
    else
        echo -e "  ${YELLOW}⊘ SKIP: MinIO bucket test (mc client not installed)${NC}"
    fi
}

# Test Keycloak
test_keycloak() {
    print_header "🔐 Keycloak Tests"
    
    test_start "Keycloak health endpoint"
    if curl -s http://localhost:8080/health/ready | grep -q "UP"; then
        test_pass
    else
        test_fail "Keycloak not healthy"
        return 1
    fi
    
    test_start "Keycloak realm accessible"
    if curl -s http://localhost:8080/realms/anki-compendium | grep -q "anki-compendium"; then
        test_pass
    else
        test_fail "Keycloak realm not configured"
    fi
    
    test_start "Keycloak admin console accessible"
    if curl -s http://localhost:8080/admin/ > /dev/null; then
        test_pass
    else
        test_fail "Keycloak admin console not accessible"
    fi
}

# Test Docker health checks
test_health_checks() {
    print_header "💚 Docker Health Checks"
    
    services=("postgres" "rabbitmq" "minio" "keycloak")
    
    for service in "${services[@]}"; do
        test_start "$service health check"
        health=$(docker-compose -f docker-compose.dev.yml ps $service | grep "healthy" || echo "not healthy")
        if echo "$health" | grep -q "healthy"; then
            test_pass
        else
            test_fail "$service is not healthy"
        fi
    done
}

# Test data persistence
test_persistence() {
    print_header "💾 Data Persistence"
    
    test_start "PostgreSQL volume exists"
    if docker volume ls | grep -q "anki_compendium_postgres_data"; then
        test_pass
    else
        test_fail "PostgreSQL volume not found"
    fi
    
    test_start "RabbitMQ volume exists"
    if docker volume ls | grep -q "anki_compendium_rabbitmq_data"; then
        test_pass
    else
        test_fail "RabbitMQ volume not found"
    fi
    
    test_start "MinIO volume exists"
    if docker volume ls | grep -q "anki_compendium_minio_data"; then
        test_pass
    else
        test_fail "MinIO volume not found"
    fi
    
    test_start "Keycloak volume exists"
    if docker volume ls | grep -q "anki_compendium_keycloak_data"; then
        test_pass
    else
        test_fail "Keycloak volume not found"
    fi
}

# Main execution
main() {
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║    Anki Compendium - Docker Compose Smoke Test Suite         ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_docker_compose
    test_postgresql
    test_rabbitmq
    test_minio
    test_keycloak
    test_health_checks
    test_persistence
    
    # Summary
    print_header "📊 Test Summary"
    echo ""
    echo "  Total Tests:  $TESTS_TOTAL"
    echo -e "  ${GREEN}Passed:       $TESTS_PASSED${NC}"
    
    if [ $TESTS_FAILED -gt 0 ]; then
        echo -e "  ${RED}Failed:       $TESTS_FAILED${NC}"
        echo ""
        echo -e "${RED}❌ Some tests failed. Please check the errors above.${NC}"
        exit 1
    else
        echo -e "  ${GREEN}Failed:       0${NC}"
        echo ""
        echo -e "${GREEN}✅ All tests passed! Environment is ready for development.${NC}"
        echo ""
        echo -e "${BLUE}Quick Access:${NC}"
        echo "  • PostgreSQL:   psql -h localhost -U $POSTGRES_USER -d $POSTGRES_DB"
        echo "  • RabbitMQ UI:  http://localhost:15672 (user: $RABBITMQ_DEFAULT_USER)"
        echo "  • MinIO Console: http://localhost:9001 (user: $MINIO_ROOT_USER)"
        echo "  • Keycloak:     http://localhost:8080"
        echo ""
    fi
}

# Run main function
main
