"""
Seed script: creates default institution, super-admin, and demo admin accounts.
Run once after initial migration:
  docker compose exec backend python scripts/seed.py
"""
import os
import sys
sys.path.insert(0, "/app")

from sqlalchemy.orm import Session
from app.database import engine
import bcrypt as bcrypt_lib

from app.models.institution import Institution
from app.models.user import User, UserRole


def hash_password(plain: str) -> str:
    """Hash a password using bcrypt directly (passlib 1.7.4 is incompatible with bcrypt 4+)."""
    return bcrypt_lib.hashpw(plain.encode("utf-8"), bcrypt_lib.gensalt()).decode("utf-8")

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
            hashed_password=hash_password(SUPER_ADMIN_PASSWORD),
            full_name="Super Admin",
            role=UserRole.super_admin,
            institution_id=None,
        )
        session.add(super_admin)
        print(f"Created super-admin: {SUPER_ADMIN_EMAIL}")
    else:
        print(f"Super-admin already exists: {SUPER_ADMIN_EMAIL}")

    # Create demo institution admin (use for AUTH-03 demo)
    existing_demo_admin = session.query(User).filter_by(email=DEMO_ADMIN_EMAIL).first()
    if not existing_demo_admin:
        demo_admin = User(
            email=DEMO_ADMIN_EMAIL,
            hashed_password=hash_password(DEMO_ADMIN_PASSWORD),
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
