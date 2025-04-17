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
from .api import auth, users, resumes, jobs, applications #, subs, visa
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(applications.router, prefix="/applications", tags=["applications"])
# app.include_router(subs.router, prefix="/subscriptions", tags=["subscriptions"])
# app.include_router(visa.router, prefix="/visa", tags=["visa"])

# Placeholder for future router includes
# from .api import auth, users, jobs, subs, visa
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(users.router, prefix="/users", tags=["users"])
# app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
# app.include_router(subs.router, prefix="/subscriptions", tags=["subscriptions"])
# app.include_router(visa.router, prefix="/visa", tags=["visa"]) 