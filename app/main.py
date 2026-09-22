from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router

app = FastAPI(title="FitBuddy - AI Fitness Plan Generator")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
