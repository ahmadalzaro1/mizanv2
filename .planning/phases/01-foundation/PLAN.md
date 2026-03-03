# Phase 1: Foundation — PLAN

> **Goal**: A developer can run the full stack locally with authentication working and the database ready to accept data.
> **Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04
> **Context file**: `.planning/phases/1-CONTEXT.md` — read this before executing any plan.
> **Stack**: Python/FastAPI (backend), React/Vite (frontend), PostgreSQL (db), Docker Compose (orchestration)
> **Repo root**: Create a new directory `mizan/` at the project root. All code lives inside it.

---

## Plan 1.1 — Project Scaffold & Docker Compose

**Goal**: The `mizan/` directory exists with the full project skeleton and `docker compose up` starts three services (db, backend, frontend) without errors. No application logic yet — just the working shell.

**Scope**: Pure scaffolding. No auth code, no DB migrations, no UI components. Just structure + Docker wiring.

---

### Instructions

Create the following directory and file structure from scratch. The project root is `/Users/ahmadalzaro/Desktop/AI Hatespeech Project/mizan/`.

#### 1. Top-level files

**`mizan/docker-compose.yml`**

```yaml
version: "3.9"

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: mizan
      POSTGRES_USER: mizan
      POSTGRES_PASSWORD: mizan_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mizan -d mizan"]
      interval: 5s
      timeout: 5s
      retries: 10

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file: .env
    environment:
      DATABASE_URL: postgresql://mizan:mizan_dev@db:5432/mizan
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file: .env
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    command: npm run dev -- --host

volumes:
  postgres_data:
```

**`mizan/.env.example`**

```
# Database
DATABASE_URL=postgresql://mizan:mizan_dev@db:5432/mizan

# JWT
JWT_SECRET=change_this_to_a_random_secret_in_production

# Frontend
VITE_API_URL=http://localhost:8000
```

**`mizan/.env`** — copy of `.env.example` with same values (used by docker compose locally). This file is gitignored.

**`mizan/.gitignore`**

```
.env
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.venv/
node_modules/
dist/
.DS_Store
*.egg-info/
```

**`mizan/README.md`**

```markdown
# Mizan (ميزان)

Arabic hate speech moderator training platform.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Services

| Service  | Port | Description              |
|----------|------|--------------------------|
| db       | 5432 | PostgreSQL 16            |
| backend  | 8000 | FastAPI + Python         |
| frontend | 5173 | React + Vite             |
```

---

#### 2. Backend scaffold

**`mizan/backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**`mizan/backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
alembic==1.13.3
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
pydantic[email]==2.9.2
pydantic-settings==2.5.2
python-dotenv==1.0.1
```

**`mizan/backend/app/__init__.py`** — empty file

**`mizan/backend/app/main.py`**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mizan API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "mizan-backend"}
```

Create empty `__init__.py` files in these directories:
- `mizan/backend/app/models/__init__.py`
- `mizan/backend/app/routers/__init__.py`
- `mizan/backend/app/schemas/__init__.py`
- `mizan/backend/app/core/__init__.py`

**`mizan/backend/alembic.ini`** — generate with `alembic init alembic` inside the container (or include manually). The key line to set:

```ini
sqlalchemy.url = %(DATABASE_URL)s
```

**`mizan/backend/alembic/env.py`** — configure to use `app.database.Base.metadata` and read `DATABASE_URL` from environment.

---

#### 3. Frontend scaffold

**`mizan/frontend/Dockerfile`**

```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
```

**`mizan/frontend/package.json`**

```json
{
  "name": "mizan-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.27.0",
    "axios": "^1.7.7"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@vitejs/plugin-react": "^4.3.3",
    "typescript": "^5.6.3",
    "vite": "^5.4.10"
  }
}
```

**`mizan/frontend/vite.config.ts`**

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
  },
})
```

**`mizan/frontend/index.html`** — standard Vite HTML entry with `<div id="root">` and link to `src/main.tsx`.

**`mizan/frontend/src/main.tsx`**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

**`mizan/frontend/src/App.tsx`**

```tsx
export default function App() {
  return <div>Mizan — loading…</div>
}
```

Create these empty placeholder directories (with `.gitkeep`):
- `mizan/frontend/src/pages/observatory/`
- `mizan/frontend/src/pages/bias-auditor/`
- `mizan/frontend/src/pages/training/`
- `mizan/frontend/src/components/`
- `mizan/frontend/src/lib/`

**`mizan/frontend/tsconfig.json`** — standard React TypeScript config with `"strict": true`.

---

### Verification for Plan 1.1

Run these commands from `mizan/`:

```bash
# Build and start all services
docker compose up --build -d

# Wait ~30s for services to start, then:

# 1. Backend health check
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"mizan-backend"}

# 2. Frontend loads
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173
# Expected: 200

# 3. Database is reachable from backend
docker compose logs backend | grep -i "application startup complete"
# Expected: startup message with no errors
```

All three checks must pass before marking this plan complete.

---

## Plan 1.2 — Database Schema & Alembic Migrations

**Goal**: The PostgreSQL database has the full Phase 1 schema: `institutions`, `users` tables, with all columns and constraints. Alembic migrations create and can roll back the schema cleanly.

**Depends on**: Plan 1.1 (Docker running, backend container exists)

---

### Instructions

#### 1. SQLAlchemy models

**`mizan/backend/app/database.py`**

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**`mizan/backend/app/models/institution.py`**

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Institution(Base):
    __tablename__ = "institutions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    users = relationship("User", back_populates="institution")
```

**`mizan/backend/app/models/user.py`**

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    moderator = "moderator"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.moderator)
    institution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="CASCADE"),
        nullable=True,  # nullable for super_admin who spans all institutions
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    institution = relationship("Institution", back_populates="users")
```

Update **`mizan/backend/app/models/__init__.py`** to import both models (so Alembic autogenerates them):

```python
from app.models.institution import Institution  # noqa: F401
from app.models.user import User, UserRole  # noqa: F401
```

#### 2. Alembic setup

Initialize Alembic inside the backend container:

```bash
docker compose exec backend alembic init alembic
```

Update **`mizan/backend/alembic/env.py`** to:
- Import `Base` from `app.database`
- Import all models from `app.models` (to register them)
- Set `target_metadata = Base.metadata`
- Read `DATABASE_URL` from `os.environ["DATABASE_URL"]`

Full `env.py`:

```python
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import all models so metadata is populated
from app.database import Base
import app.models  # noqa: F401

config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

#### 3. Generate and run migration

```bash
# Generate initial migration
docker compose exec backend alembic revision --autogenerate -m "initial schema: institutions and users"

# Run migration
docker compose exec backend alembic upgrade head
```

#### 4. Seed super-admin and demo institution

**`mizan/backend/scripts/seed.py`**

```python
"""
Seed script: creates default institution and super-admin account.
Run once after initial migration:
  docker compose exec backend python scripts/seed.py
"""
import os
import sys
sys.path.insert(0, "/app")

from sqlalchemy.orm import Session
from app.database import engine
from app.models.institution import Institution
from app.models.user import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SUPER_ADMIN_EMAIL = os.environ.get("SUPER_ADMIN_EMAIL", "admin@mizan.local")
SUPER_ADMIN_PASSWORD = os.environ.get("SUPER_ADMIN_PASSWORD", "mizan_admin_2026")
DEMO_ADMIN_EMAIL = "demo-admin@mizan.local"
DEMO_ADMIN_PASSWORD = "demo_admin_2026"
DEMO_INSTITUTION_NAME = "Demo Institution"
DEMO_INSTITUTION_SLUG = "demo"

with Session(engine) as session:
    # Create demo institution
    existing_inst = session.query(Institution).filter_by(slug=DEMO_INSTITUTION_SLUG).first()
    if not existing_inst:
        institution = Institution(name=DEMO_INSTITUTION_NAME, slug=DEMO_INSTITUTION_SLUG)
        session.add(institution)
        session.flush()
        print(f"Created institution: {DEMO_INSTITUTION_NAME} (id={institution.id})")
    else:
        institution = existing_inst
        print(f"Institution already exists: {DEMO_INSTITUTION_NAME} (id={institution.id})")

    # Create super-admin (institution_id=None — spans all institutions)
    existing_super = session.query(User).filter_by(email=SUPER_ADMIN_EMAIL).first()
    if not existing_super:
        super_admin = User(
            email=SUPER_ADMIN_EMAIL,
            hashed_password=pwd_context.hash(SUPER_ADMIN_PASSWORD),
            full_name="Super Admin",
            role=UserRole.super_admin,
            institution_id=None,
        )
        session.add(super_admin)
        print(f"Created super-admin: {SUPER_ADMIN_EMAIL}")
    else:
        print(f"Super-admin already exists: {SUPER_ADMIN_EMAIL}")

    # Create demo institution admin (demonstrates AUTH-03: admin creates moderators)
    # Use this account (not super-admin) to demo AUTH-03 in the browser.
    existing_demo_admin = session.query(User).filter_by(email=DEMO_ADMIN_EMAIL).first()
    if not existing_demo_admin:
        demo_admin = User(
            email=DEMO_ADMIN_EMAIL,
            hashed_password=pwd_context.hash(DEMO_ADMIN_PASSWORD),
            full_name="Demo Admin",
            role=UserRole.admin,
            institution_id=institution.id,
        )
        session.add(demo_admin)
        print(f"Created demo admin: {DEMO_ADMIN_EMAIL} (institution: {DEMO_INSTITUTION_SLUG})")
    else:
        print(f"Demo admin already exists: {DEMO_ADMIN_EMAIL}")

    session.commit()
    print("Seed complete.")
    print()
    print("Accounts:")
    print(f"  Super-admin:  {SUPER_ADMIN_EMAIL} / {SUPER_ADMIN_PASSWORD}")
    print(f"  Demo admin:   {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PASSWORD}  (institution: {DEMO_INSTITUTION_SLUG})")
```

---

### Verification for Plan 1.2

```bash
# Run migrations
docker compose exec backend alembic upgrade head
# Expected: "Running upgrade -> <rev_id>, initial schema: institutions and users"

# Verify tables exist in PostgreSQL
docker compose exec db psql -U mizan -d mizan -c "\dt"
# Expected: lists institutions, users, alembic_version tables

# Verify schema of users table
docker compose exec db psql -U mizan -d mizan -c "\d users"
# Expected: shows id, email, hashed_password, full_name, role, institution_id, created_at

# Run seed
docker compose exec backend python scripts/seed.py
# Expected output (in order):
#   Created institution: Demo Institution (id=...)
#   Created super-admin: admin@mizan.local
#   Created demo admin: demo-admin@mizan.local (institution: demo)
#   Seed complete.
#   Accounts:
#     Super-admin:  admin@mizan.local / mizan_admin_2026
#     Demo admin:   demo-admin@mizan.local / demo_admin_2026  (institution: demo)

# Verify seed data
docker compose exec db psql -U mizan -d mizan -c "SELECT email, role FROM users;"
# Expected: two rows — admin@mizan.local | super_admin AND demo-admin@mizan.local | admin
```

All checks must pass before marking this plan complete.

---

## Plan 1.3 — FastAPI Auth API

**Goal**: The backend exposes auth endpoints that allow login, returning a JWT, user creation by admins, and current-user lookup. All four AUTH requirements are satisfied at the API level.

**Depends on**: Plan 1.2 (database schema exists and migrations have run)

---

### Instructions

#### 1. Core settings & JWT

**`mizan/backend/app/core/config.py`**

```python
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = os.environ.get("DATABASE_URL", "")
    jwt_secret: str = os.environ.get("JWT_SECRET", "dev_secret_change_me")
    jwt_algorithm: str = "HS256"
    # No expiry for v1 — token is permanent until logout
    app_name: str = "Mizan"


settings = Settings()
```

**`mizan/backend/app/core/security.py`**

```python
from datetime import datetime
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": datetime.utcnow().isoformat(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
```

#### 2. Auth dependency

**`mizan/backend/app/core/deps.py`**

```python
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in (UserRole.admin, UserRole.super_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


def get_institution_id(current_user: User = Depends(get_current_user)):
    """
    Returns the institution_id that should scope all data queries for the current user.

    - moderator → their own institution_id (enforced, cannot be changed)
    - admin → their own institution_id
    - super_admin → None (no scoping — sees all institutions)

    Usage in routes:
        institution_id: UUID | None = Depends(get_institution_id)
        # Then filter: db.query(Content).filter(Content.institution_id == institution_id)
        # If institution_id is None (super_admin), skip the filter or return all.

    All content/session/annotation routes in Phase 2+ MUST use this dependency
    to enforce AUTH-04: moderators only see data from their institution.
    """
    if current_user.role == UserRole.super_admin:
        return None  # super_admin sees all
    return current_user.institution_id
```

#### 3. Pydantic schemas

**`mizan/backend/app/schemas/auth.py`**

```python
from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    institution_id: UUID | None

    model_config = {"from_attributes": True}


class CreateModeratorRequest(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.moderator
    institution_id: UUID | None = None  # required when super_admin creates a user
```

#### 4. Auth router

**`mizan/backend/app/routers/auth.py`**

```python
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.core.deps import get_current_user, require_admin
from app.models.user import User, UserRole
from app.models.institution import Institution
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    UserResponse,
    CreateModeratorRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(
        user_id=str(user.id),
        email=user.email,
        role=user.role.value,
    )
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.post("/users", response_model=UserResponse, status_code=201)
def create_moderator(
    request: CreateModeratorRequest,
    current_user: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    """Admin creates a moderator account within their institution.

    - Admins: new user is always attached to the admin's institution.
    - Super-admins: must provide institution_id in the request body.
    """
    if current_user.role == UserRole.super_admin:
        # Super-admin must specify which institution the new user belongs to
        if request.institution_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Super-admin must provide institution_id when creating a user",
            )
        institution_id = request.institution_id
    else:
        # Regular admin: always their own institution
        institution_id = current_user.institution_id

    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    new_user = User(
        email=request.email,
        full_name=request.full_name,
        hashed_password=hash_password(request.password),
        role=request.role,
        institution_id=institution_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    current_user: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db),
):
    """Admin lists all users in their institution."""
    if current_user.role == UserRole.super_admin:
        users = db.query(User).all()
    else:
        users = db.query(User).filter(
            User.institution_id == current_user.institution_id
        ).all()
    return users
```

#### 5. Wire router into main app

Update **`mizan/backend/app/main.py`**:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth

app = FastAPI(title="Mizan API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "mizan-backend"}
```

---

### Verification for Plan 1.3

Run the seed script first if not already done:

```bash
docker compose exec backend python scripts/seed.py
```

Then test each endpoint:

```bash
# 1. Health check
curl http://localhost:8000/health
# Expected: {"status":"ok","service":"mizan-backend"}

# 2. Login with super-admin credentials (AUTH-01, AUTH-02)
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mizan.local","password":"mizan_admin_2026"}' | python3 -m json.tool
# Expected: {"access_token": "<jwt>", "token_type": "bearer"}

# Save token to variable
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mizan.local","password":"mizan_admin_2026"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 3. Get current user (AUTH-02)
curl -s http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
# Expected: user object with email, role=super_admin

# 4. Create a moderator account as the demo-admin (AUTH-03)
# First, login as demo-admin (who has institution_id set to demo institution)
DEMO_TOKEN=$(curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo-admin@mizan.local","password":"demo_admin_2026"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

curl -s -X POST http://localhost:8000/auth/users \
  -H "Authorization: Bearer $DEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email":"moderator@demo.local","full_name":"Khaled Al-Rawi","password":"test1234","role":"moderator"}' | python3 -m json.tool
# Expected: new user object with role=moderator and institution_id matching demo institution

# 5. List users — demo-admin sees only their institution (AUTH-04 scoping)
curl -s http://localhost:8000/auth/users \
  -H "Authorization: Bearer $DEMO_TOKEN" | python3 -m json.tool
# Expected: array containing demo-admin and the new moderator — NOT the super-admin (institution_id=None)

# 6. Reject invalid login
curl -s -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@mizan.local","password":"wrong"}'
# Expected: 401 with detail "Invalid email or password"

# 7. Reject unauthenticated access
curl -s http://localhost:8000/auth/me
# Expected: 403 (no bearer token)
```

All checks must pass before marking this plan complete.

---

## Plan 1.4 — React Frontend Auth

**Goal**: The frontend has a working login page, JWT-based auth state (localStorage), protected routes, and an admin interface to create moderator accounts. A moderator who logs in stays logged in and sees their institution-scoped view.

**Depends on**: Plan 1.3 (auth API endpoints working)

---

### Instructions

#### 1. Install dependencies

The `package.json` from Plan 1.1 is already correct. After `docker compose up --build`, deps are installed. For RTL support, we do not need an additional library — CSS `dir="rtl"` and Tajawal font from Google Fonts are sufficient.

#### 2. API client

**`mizan/frontend/src/lib/api.ts`**

```typescript
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('mizan_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('mizan_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

#### 3. Auth types

**`mizan/frontend/src/lib/types.ts`**

```typescript
export type UserRole = 'super_admin' | 'admin' | 'moderator'

export interface User {
  id: string
  email: string
  full_name: string
  role: UserRole
  institution_id: string | null
}
```

#### 4. Auth context

**`mizan/frontend/src/lib/auth.tsx`**

```tsx
import React, { createContext, useContext, useEffect, useState } from 'react'
import { api } from './api'
import type { User } from './types'

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('mizan_token'))
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('mizan_token')
    if (stored) {
      api.get<User>('/auth/me')
        .then((res) => setUser(res.data))
        .catch(() => {
          localStorage.removeItem('mizan_token')
          setToken(null)
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = async (email: string, password: string) => {
    const res = await api.post<{ access_token: string }>('/auth/login', { email, password })
    const jwt = res.data.access_token
    localStorage.setItem('mizan_token', jwt)
    setToken(jwt)
    const meRes = await api.get<User>('/auth/me')
    setUser(meRes.data)
  }

  const logout = () => {
    localStorage.removeItem('mizan_token')
    setToken(null)
    setUser(null)
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
```

#### 5. Protected route component

**`mizan/frontend/src/components/ProtectedRoute.tsx`**

```tsx
import { Navigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()

  if (isLoading) return <div>جاري التحميل...</div>
  if (!user) return <Navigate to="/login" replace />

  return <>{children}</>
}
```

#### 6. Login page

**`mizan/frontend/src/pages/Login.tsx`**

```tsx
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('البريد الإلكتروني أو كلمة المرور غير صحيحة')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div dir="rtl" style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: "'Tajawal', sans-serif",
      backgroundColor: '#f5f5f5',
    }}>
      <div style={{
        background: 'white',
        padding: '2rem',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '400px',
      }}>
        <h1 style={{ textAlign: 'center', marginBottom: '1.5rem', color: '#1a1a2e' }}>
          ميزان
        </h1>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>البريد الإلكتروني</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', fontSize: '1rem', textAlign: 'right' }}
            />
          </div>
          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', marginBottom: '0.5rem' }}>كلمة المرور</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', fontSize: '1rem' }}
            />
          </div>
          {error && <p style={{ color: 'red', marginBottom: '1rem', textAlign: 'center' }}>{error}</p>}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.75rem',
              backgroundColor: '#1a1a2e',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              fontSize: '1rem',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontFamily: "'Tajawal', sans-serif",
            }}
          >
            {loading ? 'جاري تسجيل الدخول...' : 'تسجيل الدخول'}
          </button>
        </form>
      </div>
    </div>
  )
}
```

Add Tajawal font in **`mizan/frontend/index.html`** (inside `<head>`):

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
```

#### 7. Dashboard placeholder

**`mizan/frontend/src/pages/Dashboard.tsx`**

```tsx
import { useAuth } from '../lib/auth'

export default function Dashboard() {
  const { user, logout } = useAuth()

  return (
    <div dir="rtl" style={{ fontFamily: "'Tajawal', sans-serif", padding: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <h1>ميزان</h1>
        <div>
          <span style={{ marginLeft: '1rem' }}>{user?.full_name}</span>
          <button onClick={logout} style={{ padding: '0.5rem 1rem', cursor: 'pointer' }}>
            تسجيل الخروج
          </button>
        </div>
      </div>
      <nav style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <a href="/observatory">المرصد</a>
        <a href="/audit">مدقق التحيز</a>
        <a href="/train">التدريب</a>
        {(user?.role === 'admin' || user?.role === 'super_admin') && (
          <a href="/admin">الإدارة</a>
        )}
      </nav>
      <p>مرحباً بك في منصة ميزان لتدريب المشرفين على خطاب الكراهية.</p>
    </div>
  )
}
```

#### 8. Admin: Create Moderator page

**`mizan/frontend/src/pages/admin/CreateModerator.tsx`**

```tsx
import { useState } from 'react'
import { api } from '../../lib/api'

export default function CreateModerator() {
  const [form, setForm] = useState({ email: '', full_name: '', password: '', role: 'moderator' })
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const res = await api.post('/auth/users', form)
      setSuccess(`تم إنشاء الحساب بنجاح: ${res.data.email}`)
      setForm({ email: '', full_name: '', password: '', role: 'moderator' })
    } catch (err: unknown) {
      const message = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(message ?? 'حدث خطأ أثناء إنشاء الحساب')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div dir="rtl" style={{ fontFamily: "'Tajawal', sans-serif", padding: '2rem', maxWidth: '500px' }}>
      <h2>إضافة مشرف جديد</h2>
      <form onSubmit={handleSubmit}>
        {['email', 'full_name', 'password'].map((field) => (
          <div key={field} style={{ marginBottom: '1rem' }}>
            <label style={{ display: 'block', marginBottom: '0.3rem' }}>
              {field === 'email' ? 'البريد الإلكتروني' : field === 'full_name' ? 'الاسم الكامل' : 'كلمة المرور'}
            </label>
            <input
              type={field === 'password' ? 'password' : 'text'}
              value={form[field as keyof typeof form]}
              onChange={(e) => setForm({ ...form, [field]: e.target.value })}
              required
              style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc', textAlign: 'right' }}
            />
          </div>
        ))}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.3rem' }}>الدور</label>
          <select
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
          >
            <option value="moderator">مشرف</option>
            <option value="admin">مدير</option>
          </select>
        </div>
        {success && <p style={{ color: 'green', marginBottom: '1rem' }}>{success}</p>}
        {error && <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}
        <button
          type="submit"
          disabled={loading}
          style={{ padding: '0.75rem 2rem', backgroundColor: '#1a1a2e', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontFamily: "'Tajawal', sans-serif" }}
        >
          {loading ? 'جاري الإنشاء...' : 'إنشاء الحساب'}
        </button>
      </form>
    </div>
  )
}
```

#### 9. Wire up routing

**`mizan/frontend/src/App.tsx`** (final version):

```tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './lib/auth'
import { ProtectedRoute } from './components/ProtectedRoute'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import CreateModerator from './pages/admin/CreateModerator'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/admin/moderators/new" element={<ProtectedRoute><CreateModerator /></ProtectedRoute>} />
          {/* Placeholder routes for later phases */}
          <Route path="/observatory" element={<ProtectedRoute><div dir="rtl" style={{ fontFamily: 'Tajawal, sans-serif', padding: '2rem' }}>المرصد — قريباً</div></ProtectedRoute>} />
          <Route path="/audit" element={<ProtectedRoute><div dir="rtl" style={{ fontFamily: 'Tajawal, sans-serif', padding: '2rem' }}>مدقق التحيز — قريباً</div></ProtectedRoute>} />
          <Route path="/train" element={<ProtectedRoute><div dir="rtl" style={{ fontFamily: 'Tajawal, sans-serif', padding: '2rem' }}>التدريب — قريباً</div></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
```

---

### Verification for Plan 1.4

After `docker compose up` with frontend rebuilt:

```bash
# Rebuild frontend
docker compose build frontend && docker compose up -d frontend
```

Manual browser checks (open http://localhost:5173):

1. **Unauthenticated redirect** — Navigating to `http://localhost:5173/` redirects to `/login`. ✓
2. **Login form renders in Arabic RTL** — The login page shows "ميزان" heading, Arabic labels, RTL layout. ✓
3. **Invalid login shows Arabic error** — Entering wrong credentials shows "البريد الإلكتروني أو كلمة المرور غير صحيحة". ✓
4. **Successful login** — Login with `demo-admin@mizan.local` / `demo_admin_2026` redirects to dashboard. ✓
5. **Stay logged in** — Refresh the page. User remains logged in (JWT in localStorage, `/auth/me` call succeeds). ✓
6. **Create moderator (AUTH-03)** — Navigate to `/admin/moderators/new`. Fill in a new moderator's name, email, and password. Submit. Success message "تم إنشاء الحساب بنجاح: ..." appears in Arabic. The new moderator is automatically scoped to the demo institution (no institution_id field needed — admin's institution is used). ✓
7. **Logout** — Click logout button. Redirected to login. LocalStorage cleared. ✓

All 7 checks must pass before marking this plan complete.

---

## Execution Order

```
Plan 1.1 (Scaffold + Docker)
    ↓
Plan 1.2 (DB Schema + Migrations)
    ↓
Plan 1.3 (FastAPI Auth API)
    ↓
Plan 1.4 (React Frontend Auth)
```

Plans must execute in this order — each depends on the previous.

---

## Phase 1 Completion Checklist

Before marking Phase 1 complete, verify ALL success criteria from the roadmap:

- [ ] `docker compose up` starts FastAPI, React, and PostgreSQL without errors
- [ ] A new user can register (via admin create) with email and password, log in, and remain logged in across browser refreshes
- [ ] An institution admin can add a moderator account to their organization (via `/admin/moderators/new`)
- [ ] A moderator who logs in only sees content and sessions scoped to their institution (institution_id on JWT + scoped queries)
- [ ] All Arabic UI text renders RTL with Tajawal font
- [ ] API docs accessible at http://localhost:8000/docs

---

*Phase 1 PLAN — Created: 2026-03-02*
*Based on context from `.planning/phases/1-CONTEXT.md`*
