# Database Migrations Guide

This document explains how to work with Alembic database migrations in the Anki Compendium backend.

## Overview

We use **Alembic** for database schema migrations with the following configuration:
- **Async SQLAlchemy** with `asyncpg` driver for application runtime
- **Sync PostgreSQL** driver (`psycopg2`) for Alembic migrations
- **Automatic URL conversion** in `alembic/env.py` (asyncpg → psycopg2)

## Prerequisites

Ensure you have the required dependencies installed:

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Required packages:
- `alembic` - Migration framework
- `psycopg2-binary` or `psycopg2` - Sync PostgreSQL driver (for migrations)
- `asyncpg` - Async PostgreSQL driver (for application)
- `sqlalchemy[asyncio]` - SQLAlchemy with async support

## Database Connection

### Application (Async)
The FastAPI application uses async PostgreSQL connection:
```
postgresql+asyncpg://user:password@host:port/database
```

### Alembic (Sync)
Alembic migrations automatically convert to sync driver:
```
postgresql://user:password@host:port/database
```

This conversion happens automatically in `alembic/env.py` via the `get_url()` function.

## Configuration Files

### `alembic.ini`
- **DO NOT** hardcode `sqlalchemy.url` here
- URL is dynamically loaded from `app.config.settings.DATABASE_URL`
- File template uses timestamp format: `YYYYMMDD_HHMM_<rev>_<slug>`

### `alembic/env.py`
Key features:
- Imports all models to ensure metadata discovery
- Converts async URL to sync URL automatically
- Supports both online and offline migration modes
- Enables type and server default comparison

### Environment Variables
Set database URL in `.env`:
```env
DATABASE_URL=postgresql+asyncpg://ankiuser:changeme@localhost:5432/anki_compendium_dev
```

## Working with Migrations

### 1. Create a New Migration

#### Auto-generate from model changes
```bash
cd backend
alembic revision --autogenerate -m "Add new column to users table"
```

This will:
- Detect changes in SQLAlchemy models
- Generate a migration file in `alembic/versions/`
- Include upgrade and downgrade functions

#### Create empty migration
```bash
alembic revision -m "Add custom trigger"
```

### 2. Review Generated Migration

Always review the generated migration file before applying:

```bash
ls -lt alembic/versions/  # Find latest migration
cat alembic/versions/<timestamp>_<description>.py
```

Check for:
- ✅ All expected tables/columns are included
- ✅ Foreign keys are correct
- ✅ Indexes are appropriate
- ✅ Data types are correct
- ✅ Downgrade function is complete

### 3. Preview Migration (Dry Run)

Generate SQL without applying:

```bash
alembic upgrade head --sql > migration_preview.sql
```

Review `migration_preview.sql` to see exact SQL that will run.

### 4. Apply Migrations

#### Upgrade to latest version
```bash
alembic upgrade head
```

#### Upgrade/downgrade to specific revision
```bash
alembic upgrade <revision>
alembic downgrade <revision>
```

#### Downgrade one revision
```bash
alembic downgrade -1
```

### 5. Check Current Migration Status

```bash
alembic current        # Show current revision
alembic history        # Show all revisions
alembic heads          # Show head revision(s)
```

## Migration Naming Conventions

Use descriptive, action-based names:

✅ **Good Examples:**
```bash
alembic revision --autogenerate -m "Add email_verified column to users"
alembic revision --autogenerate -m "Create deck_tags junction table"
alembic revision --autogenerate -m "Add index on jobs.status"
```

❌ **Bad Examples:**
```bash
alembic revision --autogenerate -m "Update"
alembic revision --autogenerate -m "Changes"
alembic revision --autogenerate -m "Fix stuff"
```

## Common Migration Patterns

### Adding a Column

```python
def upgrade() -> None:
    op.add_column('users', 
        sa.Column('email_verified', sa.Boolean(), 
                  nullable=False, server_default='false')
    )

def downgrade() -> None:
    op.drop_column('users', 'email_verified')
```

### Creating an Index

```python
def upgrade() -> None:
    op.create_index(
        'ix_jobs_status_created_at',
        'jobs',
        ['status', 'created_at'],
        unique=False
    )

def downgrade() -> None:
    op.drop_index('ix_jobs_status_created_at', table_name='jobs')
```

### Adding PostgreSQL Extension

```python
def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgvector";')

def downgrade() -> None:
    # Usually don't drop extensions as other databases might use them
    pass
```

### Creating Trigger for `updated_at`

```python
def upgrade() -> None:
    # Create function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Create trigger
    op.execute("""
        CREATE TRIGGER update_users_updated_at
        BEFORE UPDATE ON users
        FOR EACH ROW
        EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS update_users_updated_at ON users;")
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
```

### Adding Foreign Key

```python
def upgrade() -> None:
    op.create_foreign_key(
        'fk_decks_user_id',
        'decks', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    op.drop_constraint('fk_decks_user_id', 'decks', type_='foreignkey')
```

## Initial Schema Migration

The initial migration includes:

### Tables Created
1. **users** - User accounts and subscription info
2. **decks** - Anki deck metadata
3. **jobs** - Background job tracking
4. **settings** - User-specific settings
5. **subscriptions** - Subscription history
6. **audit_logs** - Security and audit trail
7. **notifications** - User notifications

### PostgreSQL Extensions
- `uuid-ossp` - UUID generation functions
- `pgvector` - Vector similarity search (for RAG)

### Triggers
Automatic `updated_at` timestamp triggers for:
- users
- jobs
- settings
- subscriptions

### Indexes
- Primary keys (UUID)
- Foreign keys
- Status columns for queries
- Email/username for lookups
- Created_at for time-based queries

## Testing Migrations

### Test in Development

1. **Backup current state:**
   ```bash
   alembic current > current_revision.txt
   ```

2. **Apply migration:**
   ```bash
   alembic upgrade head
   ```

3. **Test application:**
   ```bash
   pytest tests/
   ```

4. **If issues, rollback:**
   ```bash
   alembic downgrade -1
   ```

### Test Full Cycle

```bash
# Start from scratch
alembic downgrade base

# Apply all migrations
alembic upgrade head

# Verify
alembic current
psql -d anki_compendium_dev -c "\dt"  # List tables
```

## Production Migration Workflow

### Pre-Deployment Checklist

- [ ] Migration tested in development environment
- [ ] Migration tested in staging environment
- [ ] Database backup created
- [ ] Migration preview SQL reviewed
- [ ] Downgrade path tested
- [ ] Team notified of schema changes
- [ ] Monitoring alerts configured

### Deployment Steps

1. **Create database backup:**
   ```bash
   pg_dump -h <host> -U <user> -d <database> -F c -f backup_$(date +%Y%m%d_%H%M%S).dump
   ```

2. **Apply migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Verify schema:**
   ```bash
   alembic current
   # Check application health endpoint
   ```

4. **If issues, rollback:**
   ```bash
   alembic downgrade <previous_revision>
   # Restore from backup if needed
   ```

## Troubleshooting

### "No module named 'psycopg2'"

```bash
pip install psycopg2-binary
```

### "Target database is not up to date"

```bash
alembic upgrade head
```

### "Can't locate revision identified by <hash>"

```bash
# Check revision history
alembic history

# If missing, may need to stamp
alembic stamp head
```

### Autogenerate not detecting changes

Ensure models are imported in `alembic/env.py`:
```python
from app.models.user import User  # noqa: F401
from app.models.deck import Deck  # noqa: F401
# ... all other models
```

### Database connection errors

Check:
1. Database is running
2. `.env` has correct `DATABASE_URL`
3. URL uses `postgresql+asyncpg://` (will be converted automatically)
4. User has proper permissions

## Best Practices

### ✅ DO

- **Always review** generated migrations before applying
- **Test migrations** in development before production
- **Create backups** before production migrations
- **Write clear commit messages** for migration files
- **Include both upgrade and downgrade** functions
- **Use descriptive migration names**
- **Keep migrations atomic** - one logical change per migration
- **Add comments** for complex SQL in migrations

### ❌ DON'T

- Don't edit applied migrations (create new ones instead)
- Don't skip migrations (apply in order)
- Don't commit generated files without review
- Don't use production database for testing
- Don't remove old migration files (breaks history)
- Don't manually alter database schema (use migrations)

## Migration File Structure

```python
"""Add email_verified to users

Revision ID: abc123def456
Revises: xyz789uvw012
Create Date: 2025-11-23 10:30:45.123456

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'abc123def456'
down_revision = 'xyz789uvw012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Apply schema changes.
    """
    # Add column
    op.add_column('users', 
        sa.Column('email_verified', sa.Boolean(), 
                  nullable=False, server_default='false')
    )


def downgrade() -> None:
    """
    Revert schema changes.
    """
    # Remove column
    op.drop_column('users', 'email_verified')
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## Support

For migration issues:
1. Check this guide
2. Review Alembic logs: `alembic upgrade head --verbose`
3. Check application logs
4. Consult team documentation
5. Contact backend team lead

---

**Last Updated:** 2025-11-23  
**Alembic Version:** 1.13.x  
**SQLAlchemy Version:** 2.0.x
