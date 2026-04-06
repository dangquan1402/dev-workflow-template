from fastapi import FastAPI

from app.features.auth.router import router as auth_router
from app.features.user.router import router as user_router
from app.features.todo.router import router as todo_router

app = FastAPI(title="Dev Workflow Template", version="0.1.0")

# --- Router registration ---
# Convention: /api/v1/{feature_name_plural}
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(todo_router, prefix="/api/v1/todos", tags=["todos"])


@app.get("/health")
async def health():
    return {"status": "ok"}
