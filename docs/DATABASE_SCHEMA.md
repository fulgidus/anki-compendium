# Anki Compendium - Database Schema

## Overview

PostgreSQL database schema for Anki Compendium application.

---

## Tables

### 1. users

Stores user account information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keycloak_id VARCHAR(255) UNIQUE NOT NULL,  -- Keycloak user ID
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE,
    display_name VARCHAR(255),
    subscription_tier VARCHAR(50) NOT NULL DEFAULT 'free',  -- 'free', 'premium'
    cards_generated_month INTEGER NOT NULL DEFAULT 0,  -- Reset monthly
    cards_limit_month INTEGER NOT NULL DEFAULT 30,  -- Free tier: 30
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE  -- Soft delete for GDPR
);

CREATE INDEX idx_users_keycloak_id ON users(keycloak_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_subscription_tier ON users(subscription_tier);
```

### 2. decks

Stores metadata about generated Anki decks.

```sql
CREATE TABLE decks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    
    name VARCHAR(255) NOT NULL,
    description TEXT,
    source_filename VARCHAR(255) NOT NULL,
    source_pages VARCHAR(100),  -- e.g., "1-10", "5,7,9-12"
    
    card_count INTEGER NOT NULL DEFAULT 0,
    file_path VARCHAR(500) NOT NULL,  -- MinIO path to .apkg file
    file_size_bytes BIGINT,
    
    language VARCHAR(10) DEFAULT 'en',  -- ISO 639-1 code
    tags TEXT[],  -- Array of tags
    
    settings JSONB,  -- Store generation settings used
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_downloaded_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_decks_user_id ON decks(user_id);
CREATE INDEX idx_decks_created_at ON decks(created_at DESC);
CREATE INDEX idx_decks_tags ON decks USING GIN(tags);
```

### 3. jobs

Tracks PDF processing jobs.

```sql
CREATE TYPE job_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'cancelled'
);

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    status job_status NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,  -- 0-100
    
    source_filename VARCHAR(255) NOT NULL,
    source_file_path VARCHAR(500) NOT NULL,  -- MinIO path to PDF
    source_file_size_bytes BIGINT,
    source_pages VARCHAR(100),  -- Page selection
    
    settings JSONB,  -- Generation settings (chunk size, models, etc.)
    
    result_deck_id UUID REFERENCES decks(id) ON DELETE SET NULL,
    error_message TEXT,
    error_stack TEXT,
    
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3
);

CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at DESC);
```

### 4. settings

Global admin-configurable settings.

```sql
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(50),  -- 'rag', 'gemini', 'limits', 'features'
    is_public BOOLEAN NOT NULL DEFAULT FALSE,  -- Visible to non-admin users
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_settings_key ON settings(key);
CREATE INDEX idx_settings_category ON settings(category);

-- Default settings
INSERT INTO settings (key, value, description, category, is_public) VALUES
    ('chunk_size_tokens', '500', 'Token count per text chunk', 'rag', false),
    ('chunk_overlap_percent', '20', 'Overlap percentage between chunks', 'rag', false),
    ('gemini_model_extraction', '"gemini-1.5-flash"', 'Model for text extraction', 'gemini', false),
    ('gemini_model_chunking', '"gemini-1.5-flash"', 'Model for chunking', 'gemini', false),
    ('gemini_model_topic_extraction', '"gemini-1.5-flash"', 'Model for topic extraction', 'gemini', false),
    ('gemini_model_qa_generation', '"gemini-1.5-flash"', 'Model for Q&A generation', 'gemini', false),
    ('gemini_model_refinement', '"gemini-1.5-pro"', 'Model for final refinement', 'gemini', false),
    ('free_tier_card_limit', '30', 'Monthly card limit for free users', 'limits', true),
    ('max_pdf_size_mb', '100', 'Maximum PDF file size in MB', 'limits', true),
    ('card_answer_min_sentences', '2', 'Minimum sentences per answer', 'rag', false),
    ('card_answer_max_sentences', '10', 'Maximum sentences per answer', 'rag', false);
```

### 5. subscriptions

User subscription and payment tracking.

```sql
CREATE TYPE subscription_status AS ENUM (
    'active',
    'cancelled',
    'expired',
    'trial'
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    tier VARCHAR(50) NOT NULL,  -- 'free', 'premium'
    status subscription_status NOT NULL DEFAULT 'active',
    
    stripe_customer_id VARCHAR(255),
    stripe_subscription_id VARCHAR(255),
    
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cancelled_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_stripe_customer_id ON subscriptions(stripe_customer_id);
```

### 6. audit_logs

Audit trail for GDPR compliance and security.

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    action VARCHAR(100) NOT NULL,  -- 'user.login', 'deck.create', 'deck.download', etc.
    resource_type VARCHAR(50),  -- 'user', 'deck', 'job'
    resource_id VARCHAR(255),
    
    ip_address INET,
    user_agent TEXT,
    
    metadata JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
```

### 7. notifications

Push notification queue and history.

```sql
CREATE TYPE notification_type AS ENUM (
    'job_completed',
    'job_failed',
    'subscription_expiring',
    'limit_reached'
);

CREATE TYPE notification_status AS ENUM (
    'pending',
    'sent',
    'failed'
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    type notification_type NOT NULL,
    status notification_status NOT NULL DEFAULT 'pending',
    
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data JSONB,  -- Additional payload
    
    push_subscription JSONB,  -- Web Push subscription details
    
    sent_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
```

---

## Relationships

```
users (1) ──< (N) decks
users (1) ──< (N) jobs
users (1) ──< (N) subscriptions
users (1) ──< (N) audit_logs
users (1) ──< (N) notifications

jobs (1) ──< (1) decks (optional, via result_deck_id)
```

---

## Indexes Summary

- **Performance**: Indexes on foreign keys, status fields, timestamps
- **Search**: GIN index on tags array for efficient tag queries
- **Audit**: Compound index on resource_type + resource_id for fast lookups

---

## Maintenance

### Auto-update timestamps

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_decks_updated_at BEFORE UPDATE ON decks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Monthly card limit reset

```sql
-- Run as cron job or scheduled task
UPDATE users SET cards_generated_month = 0;
```

---

## Migration Strategy

Use Alembic for database migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-22
