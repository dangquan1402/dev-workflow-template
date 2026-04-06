# Categories API

All endpoints require Bearer token authentication.

## POST /api/v1/categories

Create a new category for the authenticated user.

### Request Body

```json
{
  "name": "Work",
  "color": "#ff0000"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| name | string | yes | Category name (max 100 chars) |
| color | string | no | Hex color code (e.g. #ff0000) |

### Response — 201 Created

```json
{
  "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
  "name": "Work",
  "color": "#ff0000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-04-06T00:00:00",
  "updated_at": "2026-04-06T00:00:00"
}
```

## GET /api/v1/categories

List categories for the authenticated user (paginated).

### Query Parameters

| Param | Type | Default | Description |
|---|---|---|---|
| skip | int | 0 | Offset for pagination |
| limit | int | 20 | Max items per page (1-100) |

### Response — 200 OK

```json
{
  "items": [
    {
      "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
      "name": "Work",
      "color": "#ff0000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "created_at": "2026-04-06T00:00:00",
      "updated_at": "2026-04-06T00:00:00"
    }
  ],
  "total": 1
}
```

## GET /api/v1/categories/{id}

Get a single category. Must be the owner.

### Response — 200 OK

Single `CategoryResponse` object.

### Errors

- 404 — Category not found
- 403 — Not the owner

## PATCH /api/v1/categories/{id}

Update a category. Must be the owner.

### Request Body

```json
{
  "name": "Personal",
  "color": "#00ff00"
}
```

All fields are optional.

### Response — 200 OK

Updated `CategoryResponse` object.

### Errors

- 404 — Category not found
- 403 — Not the owner

## DELETE /api/v1/categories/{id}

Delete a category. Must be the owner. Also removes all todo-category associations.

### Response — 200 OK

Deleted `CategoryResponse` object.

### Errors

- 404 — Category not found
- 403 — Not the owner

## Todo Integration

### Assigning categories to todos

When creating or updating a todo, pass `category_ids` in the request body:

```json
{
  "title": "My task",
  "category_ids": ["b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e", "c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f"]
}
```

### Filtering todos by category

Use the `category_id` query parameter on `GET /api/v1/todos`:

```
GET /api/v1/todos?category_id=b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e
```
