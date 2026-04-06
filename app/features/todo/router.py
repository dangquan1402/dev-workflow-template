from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.pagination import PaginationParams
from app.features.auth.dependencies import get_current_user
from app.features.user.models import User

from . import schemas, service

router = APIRouter()


@router.post(
    "/", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED
)
async def create_todo(
    todo_in: schemas.TodoCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo_in = todo_in.model_copy(update={"user_id": current_user.id})
    return await service.create_todo(db, todo_in=todo_in)


@router.get("/", response_model=schemas.TodoListResponse)
async def list_todos(
    pagination: PaginationParams = Depends(),
    todo_status: schemas.TodoStatus | None = Query(None, alias="status"),
    category_id: int | None = Query(None),
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


@router.get("/{todo_id}", response_model=schemas.TodoResponse)
async def get_todo(
    todo_id: int,
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
    todo_id: int,
    todo_in: schemas.TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = await service.get_todo(db, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return await service.update_todo(db, db_obj=todo, todo_in=todo_in)


@router.delete("/{todo_id}", response_model=schemas.TodoResponse)
async def delete_todo(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    todo = await service.get_todo(db, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return await service.delete_todo(db, todo_id=todo_id)
