from fastapi import FastAPI

from app.features.user.router import router as user_router

app = FastAPI(title="Dev Workflow Template", version="0.1.0")

# --- Router registration ---
# Convention: /api/v1/{feature_name_plural}
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])


@app.get("/health")
async def health():
    return {"status": "ok"}
