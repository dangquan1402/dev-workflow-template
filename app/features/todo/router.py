from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.pagination import PaginationParams
from app.features.user import service as user_service

from . import schemas, service

router = APIRouter()


@router.post(
    "/", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED
)
async def create_todo(todo_in: schemas.TodoCreate, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user(db, user_id=todo_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await service.create_todo(db, todo_in=todo_in)


@router.get("/", response_model=schemas.TodoListResponse)
async def list_todos(
    pagination: PaginationParams = Depends(),
    user_id: int | None = Query(None),
    todo_status: schemas.TodoStatus | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    status_value = todo_status.value if todo_status else None
    return await service.list_todos(
        db,
        user_id=user_id,
        status=status_value,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/{todo_id}", response_model=schemas.TodoResponse)
async def get_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    todo = await service.get_todo(db, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.patch("/{todo_id}", response_model=schemas.TodoResponse)
async def update_todo(
    todo_id: int,
    todo_in: schemas.TodoUpdate,
    db: AsyncSession = Depends(get_db),
):
    todo = await service.get_todo(db, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return await service.update_todo(db, db_obj=todo, todo_in=todo_in)


@router.delete("/{todo_id}", response_model=schemas.TodoResponse)
async def delete_todo(todo_id: int, db: AsyncSession = Depends(get_db)):
    todo = await service.get_todo(db, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return await service.delete_todo(db, todo_id=todo_id)
