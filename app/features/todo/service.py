from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, schemas
from .models import Todo


async def create_todo(db: AsyncSession, todo_in: schemas.TodoCreate) -> Todo:
    return await crud.todo.create(db, obj_in=todo_in.model_dump())


async def get_todo(db: AsyncSession, todo_id: int) -> Todo | None:
    return await crud.todo.get(db, todo_id)


async def list_todos(
    db: AsyncSession,
    *,
    user_id: int | None = None,
    status: str | None = None,
    category_id: int | None = None,
    skip: int = 0,
    limit: int = 20,
) -> schemas.TodoListResponse:
    items = await crud.todo.get_filtered(
        db,
        user_id=user_id,
        status=status,
        category_id=category_id,
        skip=skip,
        limit=limit,
    )
    total = await crud.todo.count_filtered(
        db, user_id=user_id, status=status, category_id=category_id
    )
    return schemas.TodoListResponse(items=items, total=total)


async def search_todos(
    db: AsyncSession,
    *,
    user_id: int,
    query: str,
    status: str | None = None,
    category_id: int | None = None,
    skip: int = 0,
    limit: int = 20,
) -> schemas.TodoListResponse:
    items = await crud.todo.search(
        db,
        user_id=user_id,
        query=query,
        status=status,
        category_id=category_id,
        skip=skip,
        limit=limit,
    )
    total = await crud.todo.count_search(
        db,
        user_id=user_id,
        query=query,
        status=status,
        category_id=category_id,
    )
    return schemas.TodoListResponse(items=items, total=total)


async def update_todo(
    db: AsyncSession, db_obj: Todo, todo_in: schemas.TodoUpdate
) -> Todo:
    update_data = todo_in.model_dump(exclude_unset=True)
    return await crud.todo.update(db, db_obj=db_obj, obj_in=update_data)


async def delete_todo(db: AsyncSession, todo_id: int) -> Todo | None:
    return await crud.todo.delete(db, id=todo_id)
