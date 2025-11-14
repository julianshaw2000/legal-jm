# Neon + pgvector setup

This project uses PostgreSQL on Neon with the pgvector extension for embeddings.

Prerequisites:
- Neon account and project
- A database role with CREATE/ALTER permissions for running migrations

Steps:
1) Create a new Neon project and database.
2) Enable pgvector:
   - In Neon SQL console, run:
     ```
     CREATE EXTENSION IF NOT EXISTS vector;
     ```
3) Create a database role/user with permissions:
   ```
   CREATE USER app_user WITH PASSWORD 'strong-password';
   GRANT CONNECT ON DATABASE your_db TO app_user;
   GRANT USAGE ON SCHEMA public TO app_user;
   GRANT CREATE, USAGE ON SCHEMA public TO app_user;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
   ```
4) Get the connection string and set DATABASE_URL in `.env`:
   ```
   postgres://app_user:strong-password@<host>/<db>?sslmode=require
   ```
5) Run Prisma migrations and generate client from the repository root:
   ```
   npx prisma migrate dev
   npx prisma generate
   ```

Notes:
- Ensure `sslmode=require` for Neon.
- The `Embedding.vector` column uses `vector(1536)` via Prisma `Unsupported("vector(1536)")`.


