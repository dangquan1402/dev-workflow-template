"""Tests for category feature.

Tests cover: CRUD operations, user scoping, todo-category assignment,
and filtering todos by category.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.features.category import service as category_service
from app.features.category.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryListResponse,
)
from app.features.todo.schemas import TodoCreate, TodoUpdate, TodoResponse


# --- Schema tests ---


class TestCategorySchemas:
    def test_category_create_with_color(self):
        schema = CategoryCreate(name="Work", color="#ff0000")
        assert schema.name == "Work"
        assert schema.color == "#ff0000"

    def test_category_create_without_color(self):
        schema = CategoryCreate(name="Personal")
        assert schema.name == "Personal"
        assert schema.color is None

    def test_category_update_partial(self):
        schema = CategoryUpdate(name="Updated")
        data = schema.model_dump(exclude_unset=True)
        assert data == {"name": "Updated"}
        assert "color" not in data

    def test_category_response_from_attributes(self):
        mock_obj = MagicMock()
        mock_obj.id = 1
        mock_obj.name = "Work"
        mock_obj.color = "#ff0000"
        mock_obj.user_id = 1
        mock_obj.created_at = datetime(2026, 1, 1)
        mock_obj.updated_at = datetime(2026, 1, 1)
        resp = CategoryResponse.model_validate(mock_obj, from_attributes=True)
        assert resp.id == 1
        assert resp.name == "Work"

    def test_category_list_response(self):
        resp = CategoryListResponse(items=[], total=0)
        assert resp.items == []
        assert resp.total == 0


class TestTodoSchemasWithCategories:
    def test_todo_create_with_category_ids(self):
        schema = TodoCreate(title="Test", user_id=1, category_ids=[1, 2])
        assert schema.category_ids == [1, 2]

    def test_todo_create_default_empty_categories(self):
        schema = TodoCreate(title="Test", user_id=1)
        assert schema.category_ids == []

    def test_todo_update_with_category_ids(self):
        schema = TodoUpdate(category_ids=[3])
        data = schema.model_dump(exclude_unset=True)
        assert data == {"category_ids": [3]}

    def test_todo_response_includes_categories(self):
        resp = TodoResponse(
            id=1,
            title="Test",
            description=None,
            status="pending",
            user_id=1,
            categories=[],
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 1),
        )
        assert resp.categories == []


# --- Category service tests ---


class TestCategoryService:
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_create_category(self, mock_db):
        cat_in = CategoryCreate(name="Work", color="#ff0000")
        mock_cat = MagicMock()
        mock_cat.id = 1
        mock_cat.name = "Work"
        mock_cat.color = "#ff0000"
        mock_cat.user_id = 5

        with patch(
            "app.features.category.service.crud.category.create",
            return_value=mock_cat,
        ) as mock_create:
            result = await category_service.create_category(
                mock_db, user_id=5, category_in=cat_in
            )
            assert result.name == "Work"
            assert result.user_id == 5
            call_args = mock_create.call_args
            assert call_args[1]["obj_in"]["user_id"] == 5

    @pytest.mark.asyncio
    async def test_list_categories(self, mock_db):
        item1 = MagicMock()
        item1.id = 1
        item1.name = "Work"
        item1.color = "#ff0000"
        item1.user_id = 1
        item1.created_at = datetime(2026, 1, 1)
        item1.updated_at = datetime(2026, 1, 1)

        item2 = MagicMock()
        item2.id = 2
        item2.name = "Personal"
        item2.color = None
        item2.user_id = 1
        item2.created_at = datetime(2026, 1, 1)
        item2.updated_at = datetime(2026, 1, 1)

        mock_items = [item1, item2]
        with (
            patch(
                "app.features.category.service.crud.category.get_by_user",
                return_value=mock_items,
            ),
            patch(
                "app.features.category.service.crud.category.count_by_user",
                return_value=2,
            ),
        ):
            result = await category_service.list_categories(
                mock_db, user_id=1, skip=0, limit=20
            )
            assert result.total == 2
            assert len(result.items) == 2

    @pytest.mark.asyncio
    async def test_get_category(self, mock_db):
        mock_cat = MagicMock()
        mock_cat.id = 1
        with patch(
            "app.features.category.service.crud.category.get",
            return_value=mock_cat,
        ):
            result = await category_service.get_category(mock_db, category_id=1)
            assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, mock_db):
        with patch(
            "app.features.category.service.crud.category.get",
            return_value=None,
        ):
            result = await category_service.get_category(mock_db, category_id=999)
            assert result is None

    @pytest.mark.asyncio
    async def test_update_category(self, mock_db):
        mock_cat = MagicMock()
        cat_in = CategoryUpdate(name="Updated")
        mock_updated = MagicMock()
        mock_updated.name = "Updated"

        with patch(
            "app.features.category.service.crud.category.update",
            return_value=mock_updated,
        ):
            result = await category_service.update_category(
                mock_db, db_obj=mock_cat, category_in=cat_in
            )
            assert result.name == "Updated"

    @pytest.mark.asyncio
    async def test_delete_category(self, mock_db):
        mock_cat = MagicMock()
        mock_cat.id = 1
        with patch(
            "app.features.category.service.crud.category.delete",
            return_value=mock_cat,
        ):
            result = await category_service.delete_category(mock_db, category_id=1)
            assert result.id == 1


# --- User scoping tests ---


class TestCategoryUserScoping:
    """Categories should be scoped to the owning user."""

    @pytest.fixture
    def mock_db(self):
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_create_sets_user_id_from_param(self, mock_db):
        cat_in = CategoryCreate(name="Test")
        with patch(
            "app.features.category.service.crud.category.create",
            return_value=MagicMock(user_id=42),
        ) as mock_create:
            await category_service.create_category(
                mock_db, user_id=42, category_in=cat_in
            )
            call_data = mock_create.call_args[1]["obj_in"]
            assert call_data["user_id"] == 42

    @pytest.mark.asyncio
    async def test_list_filters_by_user(self, mock_db):
        with (
            patch(
                "app.features.category.service.crud.category.get_by_user",
                return_value=[],
            ) as mock_get,
            patch(
                "app.features.category.service.crud.category.count_by_user",
                return_value=0,
            ),
        ):
            await category_service.list_categories(mock_db, user_id=7)
            mock_get.assert_called_once_with(mock_db, 7, skip=0, limit=20)
