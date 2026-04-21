# Comments API

Comments are scoped to a todo. All endpoints require authentication.

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/todos/{todo_id}/comments` | Add a comment to a todo |
| GET | `/api/v1/todos/{todo_id}/comments` | List comments for a todo |
| GET | `/api/v1/todos/{todo_id}/comments/{id}` | Get a single comment |
| PATCH | `/api/v1/todos/{todo_id}/comments/{id}` | Update own comment |
| DELETE | `/api/v1/todos/{todo_id}/comments/{id}` | Delete own comment (or admin) |

## Schemas

### CommentCreate (POST body)

| Field | Type | Required | Description |
|---|---|---|---|
| body | string | yes | Comment text, min 1 char |

### CommentUpdate (PATCH body)

| Field | Type | Required | Description |
|---|---|---|---|
| body | string | no | Updated comment text |

### CommentResponse

| Field | Type | Description |
|---|---|---|
| id | int | Comment ID |
| body | string | Comment text |
| todo_id | int | Parent todo ID |
| user_id | int | Author user ID |
| created_at | datetime | |
| updated_at | datetime | |

### CommentListResponse

| Field | Type | Description |
|---|---|---|
| items | CommentResponse[] | List of comments |
| total | int | Total count |

## Errors

| Status | Condition |
|---|---|
| 401 | Not authenticated |
| 403 | Updating/deleting another user's comment (non-admin) |
| 404 | Todo or comment not found |

## Authorization

- Any authenticated user can create and list comments on any todo.
- Users can only update/delete their own comments.
- Admins can delete any comment.
