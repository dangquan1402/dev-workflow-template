from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.database import get_db
from app.common.pagination import PaginationParams
from app.features.auth.dependencies import get_current_user
from app.features.user.models import User
from app.features.user.schemas import UserRole
from app.features.todo import service as todo_service

from . import schemas, service

router = APIRouter()


async def _get_todo_or_404(db: AsyncSession, todo_id: int):
    todo = await todo_service.get_todo(db, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.post(
    "/", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED
)
async def create_comment(
    todo_id: int,
    obj_in: schemas.CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_todo_or_404(db, todo_id)
    return await service.create_comment(
        db, todo_id=todo_id, user_id=current_user.id, obj_in=obj_in
    )


@router.get("/", response_model=schemas.CommentListResponse)
async def list_comments(
    todo_id: int,
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_todo_or_404(db, todo_id)
    return await service.list_comments(
        db, todo_id=todo_id, skip=pagination.skip, limit=pagination.limit
    )


@router.get("/{comment_id}", response_model=schemas.CommentResponse)
async def get_comment(
    todo_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_todo_or_404(db, todo_id)
    comment = await service.get_comment(db, comment_id=comment_id)
    if not comment or comment.todo_id != todo_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.patch("/{comment_id}", response_model=schemas.CommentResponse)
async def update_comment(
    todo_id: int,
    comment_id: int,
    obj_in: schemas.CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_todo_or_404(db, todo_id)
    comment = await service.get_comment(db, comment_id=comment_id)
    if not comment or comment.todo_id != todo_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    return await service.update_comment(db, db_obj=comment, obj_in=obj_in)


@router.delete("/{comment_id}", response_model=schemas.CommentResponse)
async def delete_comment(
    todo_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_todo_or_404(db, todo_id)
    comment = await service.get_comment(db, comment_id=comment_id)
    if not comment or comment.todo_id != todo_id:
        raise HTTPException(status_code=404, detail="Comment not found")
    is_admin = current_user.role == UserRole.admin.value
    if comment.user_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="Not allowed")
    return await service.delete_comment(db, comment_id=comment_id)
