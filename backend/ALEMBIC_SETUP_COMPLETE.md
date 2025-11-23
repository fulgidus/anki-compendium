# Alembic Setup Summary

**Date:** 2025-11-23  
**Status:** ✅ **COMPLETE** - Ready for migration generation

---

## What Was Done

### 1. ✅ Configuration Review
Reviewed existing Alembic setup:
- `backend/alembic.ini` - Configuration file
- `backend/alembic/env.py` - Migration environment
- `backend/app/database.py` - Database connection setup
- `backend/app/models/` - 7 SQLAlchemy models

### 2. ✅ Updated `alembic.ini`
**Changes made:**
- **Removed hardcoded DATABASE_URL** (line 59)
- Added comment explaining URL is set dynamically in `env.py`
- Retained file template configuration for timestamped migrations
- Kept logging configuration intact

**Before:**
```ini
sqlalchemy.url = postgresql+asyncpg://ankiuser:changeme@localhost:5432/anki_compendium_dev
```

**After:**
```ini
# sqlalchemy.url is set dynamically in env.py from app.config.settings
# DO NOT set sqlalchemy.url here - it will be overridden in env.py
```

### 3. ✅ Updated `alembic/env.py`
**Major enhancements:**

#### Model Imports (Critical for Metadata Discovery)
```python
from app.models.user import User  # noqa: F401
from app.models.deck import Deck  # noqa: F401
from app.models.job import Job  # noqa: F401
from app.models.setting import Setting  # noqa: F401
from app.models.subscription import Subscription  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
from app.models.notification import Notification  # noqa: F401
```

⚠️ **Why this matters:** Without these imports, Alembic won't detect any tables during autogenerate!

#### Async-to-Sync URL Conversion
```python
def get_url():
    """Get database URL and convert from async to sync driver."""
    database_url = settings.DATABASE_URL
    # Convert asyncpg URL to psycopg2 URL for Alembic
    if "postgresql+asyncpg://" in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    return database_url

# Override the sqlalchemy.url in config
config.set_main_option("sqlalchemy.url", get_url())
```

**Why needed:**
- Application uses: `postgresql+asyncpg://` (async driver)
- Alembic requires: `postgresql://` (sync driver - psycopg2)
- Conversion happens automatically

#### Enhanced Migration Options
```python
context.configure(
    connection=connection,
    target_metadata=target_metadata,
    compare_type=True,              # ← Detect type changes
    compare_server_default=True,    # ← Detect default value changes
)
```

### 4. ✅ Created `MIGRATIONS.md`
Comprehensive 400+ line documentation covering:
- Overview and prerequisites
- Configuration details
- Step-by-step workflow (create, review, apply, rollback)
- Migration naming conventions
- Common patterns (columns, indexes, triggers, extensions)
- Testing procedures
- Production deployment checklist
- Troubleshooting guide
- Best practices

### 5. ✅ Documentation Structure
```
backend/
├── alembic/
│   ├── env.py              ← ✅ Updated (imports + async support)
│   ├── versions/           ← Ready for migrations
│   ├── README              ← Original Alembic docs
│   └── script.py.mako      ← Migration template
├── alembic.ini             ← ✅ Updated (removed hardcoded URL)
├── MIGRATIONS.md           ← ✅ Created (comprehensive guide)
└── .env.example            ← Already exists (reference config)
```

---

## Database Schema Overview

The system is configured to manage **7 tables**:

| Table | Purpose | Key Features |
|-------|---------|--------------|
| **users** | User accounts & auth | Keycloak integration, subscription tier, usage limits |
| **decks** | Anki deck metadata | Source PDF tracking, card count, MinIO file path |
| **jobs** | Background processing | Status tracking, error handling, result storage |
| **settings** | User preferences | Key-value config, JSONB storage |
| **subscriptions** | Payment history | Stripe integration, tier management |
| **audit_logs** | Security trail | Action tracking, IP logging |
| **notifications** | User alerts | Status, type, delivery tracking |

### Relationships
```
users (1) ──→ (N) decks
users (1) ──→ (N) jobs
users (1) ──→ (N) settings
users (1) ──→ (N) subscriptions
users (1) ──→ (N) audit_logs
users (1) ──→ (N) notifications
jobs  (1) ──→ (0-N) decks
```

---

## Next Steps

### Before Generating Migration

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

   Required packages:
   - `alembic`
   - `sqlalchemy[asyncio]>=2.0`
   - `asyncpg` - Async driver for application
   - `psycopg2-binary` - Sync driver for Alembic

2. **Setup database:**
   ```bash
   # If using docker-compose
   cd ../infra/docker-compose
   docker-compose -f docker-compose.dev.yml up -d postgres
   
   # Or setup PostgreSQL manually and ensure it's running
   ```

3. **Configure environment:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env if needed (default should work for local dev)
   ```

### Generate Initial Migration

```bash
cd backend

# Generate migration from all 7 models
alembic revision --autogenerate -m "Initial schema with users, decks, jobs, settings, subscriptions, audit_logs, notifications"
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added table 'users'
INFO  [alembic.autogenerate.compare] Detected added table 'audit_logs'
INFO  [alembic.autogenerate.compare] Detected added table 'jobs'
INFO  [alembic.autogenerate.compare] Detected added table 'settings'
INFO  [alembic.autogenerate.compare] Detected added table 'subscriptions'
INFO  [alembic.autogenerate.compare] Detected added table 'decks'
INFO  [alembic.autogenerate.compare] Detected added table 'notifications'
  Generating /path/to/backend/alembic/versions/20251123_HHMM_xxxx_initial_schema_with_users_decks_jobs_settings_subscriptions_audit_logs_notifications.py ...  done
```

### Review Generated Migration

```bash
# Find the generated file
ls -lt alembic/versions/

# Review the migration
cat alembic/versions/<timestamp>_*.py
```

**What to check:**
- ✅ All 7 tables created
- ✅ UUID columns with proper defaults
- ✅ Foreign key constraints (with CASCADE/SET NULL)
- ✅ Indexes on foreign keys and query columns
- ✅ Proper data types (UUID, ARRAY, JSONB, DateTime with timezone)
- ✅ Server defaults are set correctly

### Enhance Migration (Recommended)

Edit the generated migration to add:

#### 1. PostgreSQL Extensions
```python
def upgrade() -> None:
    # Add extensions first
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgvector";')
    
    # ... rest of table creation ...
```

#### 2. Triggers for `updated_at`
```python
def upgrade() -> None:
    # ... after table creation ...
    
    # Create update function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Add triggers for tables with updated_at
    for table in ['users', 'jobs', 'settings', 'subscriptions']:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
        """)

def downgrade() -> None:
    # Remove triggers
    for table in ['users', 'jobs', 'settings', 'subscriptions']:
        op.execute(f"DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table};")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # ... rest of table drops ...
```

### Test Migration (Dry Run)

```bash
# Preview SQL without applying
alembic upgrade head --sql > migration_preview.sql

# Review the SQL
less migration_preview.sql
```

### Apply Migration

```bash
# Apply to database
alembic upgrade head

# Verify
alembic current
psql -d anki_compendium_dev -c "\dt"  # List tables
```

### Test Rollback

```bash
# Test downgrade
alembic downgrade -1

# Verify tables removed
psql -d anki_compendium_dev -c "\dt"

# Re-apply
alembic upgrade head
```

---

## Configuration Reference

### Environment Variables (`.env`)
```env
# Database URL - Used by both app and Alembic
DATABASE_URL=postgresql+asyncpg://ankiuser:changeme@localhost:5432/anki_compendium_dev
```

**How it's used:**
- **Application:** Uses URL as-is with `asyncpg` driver
- **Alembic:** Converts to `postgresql://` (sync) automatically in `env.py`

### Alembic Commands Cheat Sheet

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head                 # Latest
alembic upgrade +1                   # One forward
alembic upgrade <revision>           # Specific

# Rollback
alembic downgrade -1                 # One back
alembic downgrade <revision>         # Specific
alembic downgrade base               # All (empty DB)

# Info
alembic current                      # Current version
alembic history                      # All revisions
alembic show <revision>              # Details

# Utilities
alembic upgrade head --sql           # Preview SQL
alembic stamp head                   # Mark as current
```

---

## Verification Checklist

Before marking this task complete, verify:

- [x] `alembic.ini` updated (hardcoded URL removed)
- [x] `alembic/env.py` updated (model imports + async support)
- [x] `MIGRATIONS.md` created (comprehensive guide)
- [x] Documentation explains URL conversion
- [x] All 7 models imported in env.py
- [ ] Dependencies installed (`pip install -r requirements-dev.txt`)
- [ ] Database running (PostgreSQL)
- [ ] Initial migration generated (`alembic revision --autogenerate`)
- [ ] Migration reviewed and enhanced
- [ ] Migration tested (dry run with `--sql`)
- [ ] Migration applied successfully

**Current Status:** Configuration complete ✅  
**Next Required Action:** Install dependencies and generate migration

---

## Troubleshooting

### Import Errors in `env.py`
**Error:** `ModuleNotFoundError: No module named 'sqlalchemy'`

**Solution:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### No Tables Detected
**Error:** `INFO  [alembic.autogenerate.compare] Detected no changes`

**Cause:** Models not imported in `env.py`

**Solution:** Already fixed! All models are now imported:
```python
from app.models.user import User  # noqa: F401
# ... all 7 models
```

### Database Connection Failed
**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
1. Ensure PostgreSQL is running
2. Check `.env` for correct DATABASE_URL
3. Verify database exists:
   ```bash
   psql -l | grep anki_compendium_dev
   ```

### Wrong Driver Error
**Error:** `No module named 'psycopg2'`

**Solution:**
```bash
pip install psycopg2-binary
```

---

## Files Modified

| File | Status | Changes |
|------|--------|---------|
| `backend/alembic.ini` | ✏️ Modified | Removed hardcoded URL (line 59) |
| `backend/alembic/env.py` | ✏️ Modified | Added model imports, async support, URL conversion |
| `backend/MIGRATIONS.md` | ✨ Created | Full migration guide (430+ lines) |

---

## Summary

✅ **Alembic is now fully configured and ready for use.**

The migration system will:
- Automatically discover all 7 tables from SQLAlchemy models
- Convert async database URL to sync URL transparently
- Support both autogenerate and manual migrations
- Enable type and default value change detection
- Work seamlessly with the async FastAPI application

**Next developer action:** Install dependencies and run `alembic revision --autogenerate` to create the initial schema migration.

---

**Setup completed by:** Developer Agent (Python/FastAPI Specialist)  
**Documentation created:** 2025-11-23  
**Alembic version:** 1.13.x  
**SQLAlchemy version:** 2.0.x (async)
