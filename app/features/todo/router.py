import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.pagination import PaginationParams
from app.common.rate_limit import rate_limit
from app.core.config import settings
from app.features.auth.dependencies import get_current_user
from app.features.user.models import User

from app.features.ws.events import notify_todo_event

from . import schemas, service

_todo_rate_limit = rate_limit(
    max_requests=settings.RATE_LIMIT_PER_MINUTE, window_seconds=60
)

router = APIRouter(dependencies=[Depends(_todo_rate_limit)])


@router.post(
    "/", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED
)
async def create_todo(
    todo_in: schemas.TodoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo_in = todo_in.model_copy(update={"user_id": current_user.id})
    todo = await service.create_todo(db, todo_in=todo_in)
    todo_data = schemas.TodoResponse.model_validate(todo).model_dump(mode="json")
    await notify_todo_event(current_user.id, "todo.created", todo_data)
    return todo


@router.get("/", response_model=schemas.TodoListResponse)
async def list_todos(
    pagination: PaginationParams = Depends(),
    todo_status: schemas.TodoStatus | None = Query(None, alias="status"),
    category_id: uuid.UUID | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status_value = todo_status.value if todo_status else None
    return await service.list_todos(
        db,
        user_id=current_user.id,
        status=status_value,
        category_id=category_id,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/search", response_model=schemas.TodoListResponse)
async def search_todos(
    q: str = Query(..., min_length=1),
    todo_status: schemas.TodoStatus | None = Query(None, alias="status"),
    category_id: uuid.UUID | None = Query(None),
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status_value = todo_status.value if todo_status else None
    return await service.search_todos(
        db,
        user_id=current_user.id,
        query=q,
        status=status_value,
        category_id=category_id,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/{todo_id}", response_model=schemas.TodoResponse)
async def get_todo(
    todo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = await service.get_todo(db, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return todo


@router.patch("/{todo_id}", response_model=schemas.TodoResponse)
async def update_todo(
    todo_id: uuid.UUID,
    todo_in: schemas.TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = await service.get_todo(db, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    updated = await service.update_todo(db, db_obj=todo, todo_in=todo_in)
    todo_data = schemas.TodoResponse.model_validate(updated).model_dump(mode="json")
    await notify_todo_event(current_user.id, "todo.updated", todo_data)
    return updated


@router.delete("/{todo_id}", response_model=schemas.TodoResponse)
async def delete_todo(
    todo_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = await service.get_todo(db, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    deleted = await service.delete_todo(db, todo_id=todo_id)
    todo_data = schemas.TodoResponse.model_validate(deleted).model_dump(mode="json")
    await notify_todo_event(current_user.id, "todo.deleted", todo_data)
    return deleted
