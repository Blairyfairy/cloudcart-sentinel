import os
os.environ.setdefault("JWT_SECRET", "test-secret-that-is-longer-than-thirty-two")
os.environ.setdefault("ADMIN_PASSWORD", "test-password")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://sentinel:sentinel@localhost:5432/sentinel")
