
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import children, activities, login_users, notifications
from app.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development (use specific domains in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(children.router)
app.include_router(activities.router)
app.include_router(login_users.router)
app.include_router(notifications.router)
