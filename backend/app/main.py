from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import hash_password
from .database import Base, SessionLocal, engine
from .models import User
from .routes import admin, login, maintenance, reports, transactions, user

app = FastAPI(title="Library Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def seed_defaults():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            db.add(
                User(
                    name="System Admin",
                    username="admin",
                    password=hash_password("admin"),
                    role="admin",
                )
            )

        normal_user = db.query(User).filter(User.username == "user").first()
        if not normal_user:
            db.add(
                User(
                    name="Default User",
                    username="user",
                    password=hash_password("user"),
                    role="user",
                )
            )
        db.commit()
    finally:
        db.close()


seed_defaults()

app.include_router(login.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(maintenance.router)
app.include_router(transactions.router)
app.include_router(reports.router)


@app.get("/")
def root():
    return {"status": "Backend running successfully"}
