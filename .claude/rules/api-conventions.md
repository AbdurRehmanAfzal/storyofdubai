# API Conventions

## REST Endpoint Structure
```
GET    /api/v1/restaurants          # List with pagination
GET    /api/v1/restaurants/{id}     # Get one
POST   /api/v1/restaurants          # Create
PUT    /api/v1/restaurants/{id}     # Update
DELETE /api/v1/restaurants/{id}     # Delete (soft)
GET    /api/v1/restaurants/search   # Filter/search
GET    /api/v1/stats                # Aggregates
```

## Request Format
```json
{
  "page": 1,
  "limit": 50,
  "sort_by": "created_at",
  "order": "desc",
  "filters": {
    "area": "downtown",
    "rating_min": 4.0,
    "is_active": true
  }
}
```

## Response Format
```json
{
  "status": "success",
  "data": {
    "items": [...],
    "total": 1234,
    "page": 1,
    "limit": 50,
    "has_more": true
  },
  "timestamp": "2026-04-20T12:00:00Z"
}
```

## Error Response
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_INPUT",
    "message": "Page must be >= 1",
    "details": {"page": "Expected integer >= 1"}
  },
  "timestamp": "2026-04-20T12:00:00Z"
}
```

## Status Codes
- **200 OK** — Successful GET, PUT
- **201 Created** — Successful POST
- **204 No Content** — Successful DELETE (soft)
- **400 Bad Request** — Invalid input
- **401 Unauthorized** — Missing/invalid token
- **403 Forbidden** — User lacks permission
- **404 Not Found** — Entity doesn't exist
- **409 Conflict** — Duplicate entry or state conflict
- **500 Internal Server Error** — Unhandled exception (log it!)
- **503 Service Unavailable** — Database/Redis down

## Query Parameters
- `page` (int, >= 1): Pagination offset
- `limit` (int, 1-100): Items per page, default 50
- `sort_by` (str): Column name
- `order` (str): 'asc' or 'desc'
- `q` (str): Full-text search query
- `filter_*` (str): Resource-specific filters (e.g., ?filter_area=downtown)

## Authentication
- **Header**: `Authorization: Bearer <jwt_token>`
- **Token lifetime**: 7 days (refresh before expiry)
- **Secret**: Stored in .env as SECRET_KEY

## Rate Limiting
- **Global**: 1000 requests/hour per IP
- **Scraper endpoints**: 10 requests/minute (prevent accidental DoS)
- **Headers**: Return X-RateLimit-Remaining, X-RateLimit-Reset
