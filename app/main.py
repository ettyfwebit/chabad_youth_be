
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.routers import attendance, branch_managers, branches, children, activities, classgrades, groups, login_users, meetings, notifications, parents, shirts
from app.database import Base, engine
from fastapi.staticfiles import StaticFiles
import os
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


import os
app.mount("/static", StaticFiles(directory=os.path.join("C:\\", "Users", "Riky", "Desktop", "chabad_youth_fe", "build", "static")), name="static")

# מסלול עבור קובץ ה-HTML הראשי של React
@app.get("/")
async def index():
    return FileResponse(os.path.join(os.getcwd(), "C:\\", "Users", "Riky", "Desktop", "chabad_youth_fe","build", "index.html"))

# Include routers
app.include_router(children.router)
app.include_router(activities.router)
app.include_router(login_users.router)
app.include_router(notifications.router)
app.include_router(branches.router)
app.include_router(classgrades.router)
app.include_router(shirts.router)
app.include_router(groups.router)
app.include_router(meetings.router)
app.include_router(attendance.router)
app.include_router(branch_managers.router)
app.include_router(parents.router)
