from fastapi import FastAPI

from app.features.auth.router import router as auth_router
from app.features.category.router import router as category_router
from app.features.comment.router import router as comment_router
from app.features.oauth.router import router as oauth_router
from app.features.user.router import router as user_router
from app.features.todo.router import router as todo_router
from app.features.ws.router import router as ws_router

app = FastAPI(title="Dev Workflow Template", version="0.1.0")

# --- Router registration ---
# Convention: /api/v1/{feature_name_plural}
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(oauth_router, prefix="/api/v1/auth/oauth", tags=["oauth"])
app.include_router(user_router, prefix="/api/v1/users", tags=["users"])
app.include_router(todo_router, prefix="/api/v1/todos", tags=["todos"])
app.include_router(category_router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(
    comment_router, prefix="/api/v1/todos/{todo_id}/comments", tags=["comments"]
)
app.include_router(ws_router, tags=["websocket"])


@app.get("/health")
async def health():
    return {"status": "ok"}
