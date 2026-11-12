# Database Migration Guide (Proxam AI)

This guide documents the current database setup and Alembic migration workflow for Proxam AI. It is based on the repository state and is intended for developers working in the `backend/` directory.

> **Scope:** Documentation only. This guide does not modify application code, configuration, migration files, or database contents.

---

## 1. Current Database Setup

### Database engines
- **SQLite** is the default development database (`backend/app/config.py:15`): `database_url = "sqlite:///./proxam_ai.db"`.
- **PostgreSQL** is supported via `DATABASE_URL` and `psycopg2-binary` dependency (`backend/requirements.txt:5`).

### Connection and runtime behavior
- `backend/app/database.py`:
  - Creates SQLAlchemy engine from `settings.database_url` (line 12-16).
  - Adds `check_same_thread=False` for SQLite (lines 8-10).
  - Enables `PRAGMA foreign_keys=ON` for SQLite connections via connect event (lines 19-25).
  - Provides `create_db_and_tables()` which runs `SQLModel.metadata.create_all(engine)` (lines 27-29).
- `backend/app/main.py`:
  - Application lifespan calls `create_db_and_tables()` at startup (lines 18-23).

### Active database path (observed during prior audit)
- When running from `backend/`, the relative SQLite path `./proxam_ai.db` resolves to `backend/proxam_ai.db`.
- A separate `proxam_ai.db` also exists at the project root. **Do not assume the root file is the active database**; always verify `DATABASE_URL` and working directory.

---

## 2. Alembic Configuration and Migration History

### Configuration files
- `backend/alembic.ini`:
  - `script_location = alembic` (line 2)
  - `prepend_sys_path = .` (line 3)
  - `file_template = %(year)d%(month).2d%(day).2d_%(hour).2d%(minute).2d_%(rev)s_%(slug)s` (line 5)
  - `timezone = UTC` (line 6)
- `backend/alembic/env.py`:
  - Inserts backend parent into `sys.path` and imports app settings/models (lines 9-12)
  - Sets `sqlalchemy.url` from `settings.database_url` (lines 19-20)
  - Uses `SQLModel.metadata` as `target_metadata` for autogenerate (line 22)
  - Supports offline and online migration modes (lines 25-53)

### Migration history (versions in `backend/alembic/versions/`)
| Revision | File | Revises | Purpose |
|----------|------|---------|---------|
| `attempt_created_status_nullable_timestamps` | `attempt_created_status_nullable_timestamps.py` | `None` (base) | Makes `attempts.started_at` and `attempts.time_limit_ends_at` nullable; adds `attempts.created_at` |
| `add_attempt_foreign_keys_and_unique_constraint` | `add_attempt_foreign_keys_and_unique_constraint.py` | `attempt_created_status_nullable_timestamps` | Adds FKs `attempts.test_id→tests.id`, `attempts.student_id→users.id`; adds unique constraint `uq_student_test_attempt(student_id, test_id)` |
| `6520861a8d45` (head) | `20261101_0612_6520861a8d45_add_unique_constraint_answers_attempt_question.py` | `add_attempt_foreign_keys_and_unique_constraint` | Adds unique constraint `uq_answers_attempt_question(attempt_id, question_id)` on `answers` |

**Current head:** `6520861a8d45`

> **Note:** The migration chain is linear. All migrations use `batch_alter_table` for SQLite compatibility.

---

## 3. Checking Current Migration Revision

Run from the `backend/` directory in PowerShell.

### Check heads and history
```powershell
cd "C:\Users\HP\Desktop\Proxam AI\backend"
python -m alembic -c alembic.ini heads
python -m alembic -c alembic.ini history --verbose
```

### Check current database revision
```powershell
cd "C:\Users\HP\Desktop\Proxam AI\backend"
python -m alembic -c alembic.ini current
```

**Important:** `alembic/env.py` loads settings via `get_settings()` (which requires `SECRET_KEY`). Ensure `.env` is configured or `SECRET_KEY` is set in the environment before running Alembic commands that load the app config.

### Windows/PowerShell shadowing note
There is a local `backend/alembic/` package directory. Running `alembic` or `python -m alembic` from certain locations can fail with module resolution issues (e.g., `Path doesn't exist: alembic` or shadowing of the installed `alembic` package).

**Recommended approaches:**
1. Run from `backend/` with explicit config: `python -m alembic -c alembic.ini <command>`
2. If module shadowing occurs, run from project root and set script location explicitly:
```powershell
cd "C:\Users\HP\Desktop\Proxam AI"
python -c "from alembic.config import Config; from alembic import command; cfg=Config('backend/alembic.ini'); cfg.set_main_option('script_location','backend/alembic'); command.current(cfg)"
```

Always verify you are targeting the correct database (`DATABASE_URL` and working directory).

---

## 4. Generating a New Migration

### Prerequisites
- Models are updated in `backend/app/models/` (and imported so `SQLModel.metadata` includes them).
- `SECRET_KEY` is available (via `.env` or environment) because `alembic/env.py` loads settings.
- You understand the intended schema change.

### Autogenerate command (PowerShell)
```powershell
cd "C:\Users\HP\Desktop\Proxam AI\backend"
python -m alembic -c alembic.ini revision --autogenerate -m "describe_change_here"
```

### Manual migration (when autogenerate is insufficient)
```powershell
cd "C:\Users\HP\Desktop\Proxam AI\backend"
python -m alembic -c alembic.ini revision -m "describe_change_here"
```

**Notes:**
- Autogenerate compares `SQLModel.metadata` (target) against the database schema. It may miss some changes (e.g., certain constraint types, server defaults, or SQLite-specific alterations).
- SQLite has limited `ALTER TABLE` support; prefer `batch_alter_table` operations (as existing migrations do).

---

## 5. Inspecting and Reviewing Generated Migration Files

Before applying any migration:

1. **Open the generated file** in `backend/alembic/versions/`.
2. **Verify revision chain:**
   - `revision` is unique
   - `down_revision` points to the expected previous head
3. **Review `upgrade()` and `downgrade()`:**
   - Confirm intended schema changes only
   - Check for data-destructive operations (`drop_table`, `drop_column`, type changes)
   - For SQLite, ensure batch operations are used where required
4. **Check for unintended changes:** Autogenerate can produce spurious diffs; remove anything not related to the intended change.
5. **Validate downgrade path:** Ensure `downgrade()` is feasible and safe for your environment (or document if irreversible).
6. **Test in a copy/dev database first** — never test on production data.

---

## 6. Creating a Database Backup Before Applying Migrations

**Always back up before applying migrations.**

### SQLite (development) — PowerShell
```powershell
# Stop the application first to avoid locks
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item "C:\Users\HP\Desktop\Proxam AI\backend\proxam_ai.db" "C:\Users\HP\Desktop\Proxam AI\backend\proxam_ai.db.backup_$timestamp"
```

Verify the backup exists and is non-empty before proceeding.

### PostgreSQL (production/staging)
Use `pg_dump` with appropriate credentials and connection parameters. Example pattern:
```powershell
# Example only - adjust host, port, user, and database name
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
pg_dump --host=<host> --port=<port> --username=<user> --format=custom --file="proxam_ai_backup_$timestamp.dump" <database_name>
```

**Do not** store credentials in scripts committed to the repository. Use environment variables or secure credential management.

---

## 7. Applying Migrations

```powershell
cd "C:\Users\HP\Desktop\Proxam AI\backend"
python -m alembic -c alembic.ini upgrade head
```

To upgrade to a specific revision:
```powershell
python -m alembic -c alembic.ini upgrade <revision_id>
```

**Rules:**
- Apply migrations deliberately and manually.
- **Never** run migrations automatically during application startup.
- Ensure the correct `DATABASE_URL` and working directory are in use.
- Prefer applying migrations during a maintenance window for production.

---

## 8. Verifying Resulting Database Revision and Schema

### Verify Alembic revision
```powershell
cd "C:\Users\HP\Desktop\Proxam AI\backend"
python -m alembic -c alembic.ini current
python -m alembic -c alembic.ini heads
```
`current` should match `head` after a successful upgrade.

### Verify schema (read-only, SQLite example)
```powershell
python -c "import sqlite3; conn=sqlite3.connect('proxam_ai.db'); c=conn.cursor(); c.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\"); print([r[0] for r in c.fetchall()]); c.execute('PRAGMA foreign_key_list(attempts)'); print(c.fetchall()); c.execute('PRAGMA index_list(answers)'); print(c.fetchall()); conn.close()"
```

Check that:
- Expected tables exist
- Foreign keys and unique constraints are present
- `alembic_version` contains the expected revision

### Verify schema (PostgreSQL)
Use `psql` or a DB client to inspect `information_schema`, constraints, and indexes. Confirm `alembic_version.version_num` matches head.

---

## 9. Downgrading Safely (Including Risks)

### Downgrade commands
```powershell
cd "C:\Users\HP\Desktop\Proxam AI\backend"
# Downgrade one revision
python -m alembic -c alembic.ini downgrade -1

# Downgrade to a specific revision
python -m alembic -c alembic.ini downgrade <revision_id>

# Downgrade to base (removes all applied revisions) — DANGEROUS
python -m alembic -c alembic.ini downgrade base
```

### Risks
- **Data loss:** Downgrades that drop columns/tables/constraints can permanently remove data.
- **Irreversible operations:** Some migrations cannot be safely reversed; `downgrade()` may be incomplete or destructive.
- **Constraint violations:** Reverting constraints may fail if existing data no longer satisfies the older schema.
- **SQLite table rebuilds:** Batch operations recreate tables; ensure backups exist.
- **Application incompatibility:** Older application code may not work with a downgraded schema (and vice versa).

**Always** back up before downgrading and test the downgrade path in a non-production environment.

---

## 10. What Developers Must Never Do

- **Never delete the database** to "fix" migration issues.
- **Never blindly run `alembic stamp`** to force the version table to match head without verifying the actual schema.
- **Never manually modify migration history** in `alembic_version` unless you fully understand the consequences and have a verified recovery plan.
- **Never edit applied migration files** that have already been run in shared environments; create a new migration instead.
- **Never run migrations automatically during application startup.**
- **Never assume** `SQLModel.metadata.create_all()` keeps schema in sync with migrations.
- **Never apply migrations without a backup.**
- **Never run migrations against the wrong database**; always confirm `DATABASE_URL` and working directory.
- **Never commit secrets** (`.env`, credentials, tokens) to version control.

---

## 11. `SQLModel.metadata.create_all()` and Alembic

### Current behavior
- `backend/app/database.py:27-29` defines `create_db_and_tables()` which calls `SQLModel.metadata.create_all(engine)`.
- `backend/app/main.py:18-23` calls `create_db_and_tables()` in the FastAPI lifespan on every startup.

### What `create_all()` does
- Creates tables that do not exist based on current SQLModel metadata.
- **Does not** alter existing tables to match model changes.
- **Does not** create, update, or track Alembic migration revisions.
- **Does not** drop removed tables/columns.

### Relationship with Alembic
- **Alembic** is the source of truth for schema evolution: it generates and applies incremental, versioned migration scripts.
- **`create_all()`** is a convenience for bootstrapping missing tables in development but is not a migration mechanism.

### Schema drift risk
Because `create_all()` runs at startup and Alembic migrations are applied manually:
- A database created/modified by `create_all()` may diverge from the migration history.
- New model fields/constraints may exist in code but not in the database (if no migration was applied), or vice versa.
- The `alembic_version` table may not reflect the actual schema state if migrations are not applied consistently.

**Recommended practice:**
- Treat Alembic migrations as required for all schema changes.
- Use `create_all()` only for initial local bootstrapping when appropriate, and prefer `alembic upgrade head` for consistent environments.
- Consider disabling or gating `create_all()` in production once a migration workflow is fully adopted (documented concern; no code change made).

### Known concern (documented, not fixed)
- Application startup still invokes `create_all()` (`main.py:21`). This can mask missing migrations in development and contribute to schema drift. A future improvement would be to rely exclusively on Alembic migrations for schema management in all environments.
