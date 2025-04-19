from fastapi import FastAPI

app = FastAPI(
    title="JobBright API",
    description="API for the JobBright application.",
    version="0.1.0",
)

@app.get("/")
async def root():
    return {"message": "Welcome to JobBright API"}

# Include API routers
from .api import users, resumes, jobs, applications, visa, subs # Added visa & subs import
# app.include_router(auth.router, prefix="/auth", tags=["auth"]) # Auth handled by middleware/dependency now
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
app.include_router(subs.router, prefix="/subscriptions", tags=["subscriptions"]) # Uncommented subs router
app.include_router(visa.router, prefix="/visa", tags=["visa"]) # Uncommented visa router

# Placeholder for future router includes
# from .api import auth, users, jobs, subs
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(users.router, prefix="/users", tags=["users"])
# app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
# app.include_router(subs.router, prefix="/subscriptions", tags=["subscriptions"])
# app.include_router(visa.router, prefix="/visa", tags=["visa"])
