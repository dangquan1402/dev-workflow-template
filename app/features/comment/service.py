from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, schemas
from .models import Comment


async def create_comment(
    db: AsyncSession, todo_id: int, user_id: int, obj_in: schemas.CommentCreate
) -> Comment:
    return await crud.comment.create(
        db, obj_in={**obj_in.model_dump(), "todo_id": todo_id, "user_id": user_id}
    )


async def get_comment(db: AsyncSession, comment_id: int) -> Comment | None:
    return await crud.comment.get(db, comment_id)


async def list_comments(
    db: AsyncSession, todo_id: int, skip: int = 0, limit: int = 20
) -> schemas.CommentListResponse:
    items = await crud.comment.get_by_todo(db, todo_id, skip=skip, limit=limit)
    total = await crud.comment.count_by_todo(db, todo_id)
    return schemas.CommentListResponse(items=items, total=total)


async def update_comment(
    db: AsyncSession, db_obj: Comment, obj_in: schemas.CommentUpdate
) -> Comment:
    update_data = obj_in.model_dump(exclude_unset=True)
    return await crud.comment.update(db, db_obj=db_obj, obj_in=update_data)


async def delete_comment(db: AsyncSession, comment_id: int) -> Comment | None:
    return await crud.comment.delete(db, id=comment_id)
