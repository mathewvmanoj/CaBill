import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.database import DatabaseConnection
from app.migration import run_migration


# Initialize FastAPI app
app = FastAPI(
    title="Fintrack - An Invoice Automation System",
    description=(
        "Fintrack is a powerful and scalable invoice automation system built with FastAPI. "
        "It integrates MongoDB for efficient data storage and utilizes JWT authentication "
        "for secure access control. With automated invoice tracking, real-time updates, "
        "and role-based user management, Fintrack streamlines financial operations while "
        "ensuring data integrity and security."
    ),
    version="1.0.0",
)

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])

# CORS Middleware (Allow frontend requests)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database connection
from app.database import DatabaseConnection

@app.on_event("startup")
async def startup_event():
    await DatabaseConnection.connect()
    
    # Check if migration has already run (for example, check if a specific collection or document exists)
    migration_done = await DatabaseConnection.db.migrations.find_one({"name": "initial_migration"})
    
    if not migration_done:
        print("Running migration...")
        await run_migration()
        
        # Mark migration as done
        await DatabaseConnection.db.migrations.insert_one({"name": "initial_migration"})
        print("Migration completed and recorded.")

@app.on_event("shutdown")
async def shutdown_event():
    await DatabaseConnection.close()

# Root Route
@app.get("/")
async def root():
    return {"message": "Welcome to Invoice Automation Backend!"}

# Run the app on port 8000
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)