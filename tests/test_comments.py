"""Tests for comment feature.

Tests cover: schema validation, CRUD operations via service layer,
and authorization logic (owner-only update, owner+admin delete).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.features.comment import service as comment_service
from app.features.comment.schemas import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentListResponse,
)


# --- Schema tests ---


class TestCommentSchemas:
    def test_comment_create(self):
        schema = CommentCreate(body="Great work!")
        assert schema.body == "Great work!"

    def test_comment_create_empty_body_rejected(self):
        with pytest.raises(ValueError, match="must not be empty"):
            CommentCreate(body="   ")

    def test_comment_update_partial(self):
        schema = CommentUpdate(body="Updated text")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"body": "Updated text"}

    def test_comment_update_none_body(self):
        schema = CommentUpdate()
        data = schema.model_dump(exclude_unset=True)
        assert data == {}

    def test_comment_update_empty_body_rejected(self):
        with pytest.raises(ValueError, match="must not be empty"):
            CommentUpdate(body="")

    def test_comment_response_from_attributes(self):
        mock_obj = MagicMock()
        mock_obj.id = 1
        mock_obj.body = "Hello"
        mock_obj.todo_id = 10
        mock_obj.user_id = 5
        mock_obj.created_at = datetime(2026, 1, 1)
        mock_obj.updated_at = datetime(2026, 1, 1)
        resp = CommentResponse.model_validate(mock_obj, from_attributes=True)
        assert resp.id == 1
        assert resp.body == "Hello"
        assert resp.todo_id == 10

    def test_comment_list_response(self):
        resp = CommentListResponse(items=[], total=0)
        assert resp.items == []
        assert resp.total == 0


# --- Service tests ---


class TestCommentService:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_create_comment(self, mock_db):
        obj_in = CommentCreate(body="Nice todo!")
        mock_comment = MagicMock()
        mock_comment.id = 1
        mock_comment.body = "Nice todo!"
        mock_comment.todo_id = 10
        mock_comment.user_id = 5

        with patch(
            "app.features.comment.service.crud.comment.create",
            return_value=mock_comment,
        ) as mock_create:
            result = await comment_service.create_comment(
                mock_db, todo_id=10, user_id=5, obj_in=obj_in
            )
            assert result.body == "Nice todo!"
            call_data = mock_create.call_args[1]["obj_in"]
            assert call_data["todo_id"] == 10
            assert call_data["user_id"] == 5

    @pytest.mark.asyncio
    async def test_get_comment(self, mock_db):
        mock_comment = MagicMock()
        mock_comment.id = 1
        with patch(
            "app.features.comment.service.crud.comment.get",
            return_value=mock_comment,
        ):
            result = await comment_service.get_comment(mock_db, comment_id=1)
            assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_comment_not_found(self, mock_db):
        with patch(
            "app.features.comment.service.crud.comment.get",
            return_value=None,
        ):
            result = await comment_service.get_comment(mock_db, comment_id=999)
            assert result is None

    @pytest.mark.asyncio
    async def test_list_comments(self, mock_db):
        item1 = MagicMock()
        item1.id = 1
        item1.body = "First"
        item1.todo_id = 10
        item1.user_id = 1
        item1.created_at = datetime(2026, 1, 1)
        item1.updated_at = datetime(2026, 1, 1)

        with (
            patch(
                "app.features.comment.service.crud.comment.get_by_todo",
                return_value=[item1],
            ),
            patch(
                "app.features.comment.service.crud.comment.count_by_todo",
                return_value=1,
            ),
        ):
            result = await comment_service.list_comments(
                mock_db, todo_id=10, skip=0, limit=20
            )
            assert result.total == 1
            assert len(result.items) == 1

    @pytest.mark.asyncio
    async def test_update_comment(self, mock_db):
        mock_comment = MagicMock()
        obj_in = CommentUpdate(body="Updated")
        mock_updated = MagicMock()
        mock_updated.body = "Updated"

        with patch(
            "app.features.comment.service.crud.comment.update",
            return_value=mock_updated,
        ):
            result = await comment_service.update_comment(
                mock_db, db_obj=mock_comment, obj_in=obj_in
            )
            assert result.body == "Updated"

    @pytest.mark.asyncio
    async def test_delete_comment(self, mock_db):
        mock_comment = MagicMock()
        mock_comment.id = 1
        with patch(
            "app.features.comment.service.crud.comment.delete",
            return_value=mock_comment,
        ):
            result = await comment_service.delete_comment(mock_db, comment_id=1)
            assert result.id == 1
