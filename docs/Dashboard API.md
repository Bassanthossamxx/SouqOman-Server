# Dashboard API Documentation

> Base URL: `/dashboard/`
> Authentication: JWT Bearer Token (Required)
> Authorization: Superuser access only (`is_superuser = true`)

---

## Pagination

All list endpoints in the dashboard are paginated with a fixed page size of 20 items per page. Use the `page` query parameter to navigate (1-indexed). The response shape is:
```
{
  "count": <total_items>,
  "next": "<url or null>",
  "previous": "<url or null>",
  "results": [ ...items... ]
}
```

---

## Quick Reference

| Endpoint                   | Method | Description |
|----------------------------|--------|-------------|
| `/login/`                  | POST | Superuser login (returns JWT tokens; uses phone) |
| `/token/refresh/`          | POST | Refresh access token (JWT) |
| `/token/verify/` | POST | Verify JWT token validity |
| `/products/`               | GET | List all products (all statuses) |
| `/products/{id}/approve/`  | PATCH or PUT | Approve pending product (no body required) |
| `/products/{id}/`          | DELETE | Hard delete product |
| `/categories/`             | POST | Create category |
| `/subcategories/`          | POST | Create subcategory |
| `/ads/`                    | GET | List all ad requests |
| `/ads/{id}/approve/`       | PATCH | Approve ad request |
| `/users/`                  | GET | List all users |
| `/users/{id}/`             | GET | Get user details |
| `/users/{id}/`             | PATCH | Update user |
| `/users/{id}/`             | DELETE | Delete user |

---
##  Authentication

All endpoints require JWT Bearer authentication.

#### Request Header Format

```
Authorization: Bearer <your_access_token>
```

#### Common Authentication Errors

| Status | Description | Response |
|--------|-------------|----------|
| `401` | No token provided | `{"detail": "Authentication credentials were not provided."}` |
| `401` | Invalid/expired token | `{"detail": "Given token not valid for any token type", "code": "token_not_valid"}` |
| `403` | Not a superuser | `{"detail": "You do not have permission to perform this action."}` |

---

## Superuser Login

### `POST /dashboard/login/`

Authenticate as a superuser to access dashboard endpoints. Returns JWT tokens if credentials are valid and user is a superuser.

**Request Body:**
```json
{
  "phone": "string",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Invalid credentials or not a superuser."
}
```

**Notes:**
- Only users with `is_superuser = true` can log in.
- Use the `access` token as a Bearer token for authenticated requests.
- The phone field is used for login instead of username.

---

## Token Management

### `POST /dashboard/token/refresh/`

Obtain a new access token using a valid refresh token.

**Request Body:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response (200 OK):**
```json
{
  "access": "<new_access_token>"
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired"
}
```

### `POST /dashboard/token/verify/`

Verify if a JWT token is valid.

**Request Body:**
```json
{
  "token": "<access_or_refresh_token>"
}
```

**Response (200 OK):**
```json
{}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Token is invalid or expired"
}
```


## Product Management

### List All Products

| | |
|---|---|
| Endpoint | `GET /dashboard/products/` |
| Auth Required | Yes (Superuser) |
| Request Body | None |

#### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `search` | string | No | Search in product name, category, subcategory | `?search=laptop` |
| `category` | integer | No | Filter by category ID | `?category=5` |
| `subcategory` | integer | No | Filter by subcategory ID | `?subcategory=12` |
| `status` | string | No | Filter by status: `active`, `pending`, `inactive` | `?status=pending` |
| `min_price` | decimal | No | Minimum price | `?min_price=100` |
| `max_price` | decimal | No | Maximum price | `?max_price=1000` |
| `ordering` | string | No | Sort: `price`, `-price`, `posted_at`, `-posted_at`, `views_count`, `-views_count` | `?ordering=-posted_at` |

#### Response

Status: `200 OK`

```json
{
  "count": 150,
  "next": "http://localhost:8000/dashboard/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 45,
      "user": {
        "id": 12,
        "phone": "96812345678",
        "full_name_ar": "محمد أحمد",
        "full_name_en": "Mohammed Ahmed"
      },
      "category": {
        "id": 5,
        "name_en": "Electronics",
        "name_ar": "إلكترونيات",
        "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/category.jpg"
      },
      "subcategory": {
        "id": 12,
        "name_en": "Laptops",
        "name_ar": "حواسيب محمولة",
        "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/subcategory.jpg"
      },
      "name_en": "Dell Laptop",
      "name_ar": "حاسوب ديل",
      "description_en": "High performance laptop",
      "description_ar": "حاسوب عالي الأداء",
      "price": "450.00",
      "phone": "96898765432",
      "whatsapp": "96898765432",
      "images": [
        { "id": 78, "image": "https://res.cloudinary.com/xxx/image.jpg" }
      ],
      "status": "active",
      "posted_at": "2025-10-09T10:30:00Z",
      "views_count": 125,
      "ad": false,
      "ad_start": null,
      "ad_end": null
    }
  ]
}
```

---

### Approve Pending Product

| | |
|---|---|
| Endpoint | `PATCH /dashboard/products/{id}/approve/` or `PUT /dashboard/products/{id}/approve/` |
| Auth Required | Yes (Superuser) |
| Request Body | None |

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Product ID to approve |

#### Response

Status: `200 OK`

```json
{
  "message": "Product 'حاسوب ديل' approved and activated."
}
```

#### Errors

| Status | Description |
|--------|-------------|
| `401` | Missing or invalid authentication token |
| `403` | User is not a superuser |
| `404` | Product not found or not in pending status |

---

### Delete Product (Hard Delete)

| | |
|---|---|
| Endpoint | `DELETE /dashboard/products/{id}/` |
| Auth Required | Yes (Superuser) |
| Request Body | None |

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Product ID to delete |

#### Response

Status: `204 No Content`

No response body returned on success.

#### Errors

| Status | Description | Response Example |
|--------|-------------|------------------|
| `401` | Missing or invalid authentication token | `{"detail": "Authentication credentials were not provided."}` |
| `403` | User is not a superuser | `{"detail": "You do not have permission to perform this action."}` |
| `404` | Product not found | `{"detail": "Not found."}` |

---

## Categories & Subcategories (Admin)

### Create Category

| | |
|---|---|
| Endpoint | `POST /dashboard/categories/` |
| Auth Required | Yes (Superuser) |
| Content-Type | `multipart/form-data` |

#### Request Body (Form Data)

```
name_en: "Electronics" (required)
name_ar: "إلكترونيات" (required)
image: <file> (optional)
```

#### Field Requirements

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name_en` | string | Yes | Category name in English (only English letters and spaces) |
| `name_ar` | string | Yes | Category name in Arabic (only Arabic letters and spaces) |
| `image` | file | No | Category image (uploaded to Cloudinary, returns image_url) |

#### Response

Status: `201 Created`

```json
{ "id": 5, "name_en": "Electronics", "name_ar": "إلكترونيات", "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/category.jpg" }
```

**Note:** If no image is uploaded, `image_url` will be an empty string `""`.

#### Errors

| Status | Description | Response Example |
|--------|-------------|------------------|
| `400` | Validation error (empty or invalid names) | `{"name_en": ["This field may not be blank."]}` |
| `400` | Duplicate category name | `{"name_en": ["Category with this name already exists."]}` or `{"name_ar": ["Category with this name already exists."]}` |
| `401` | Missing or invalid authentication token | `{"detail": "Authentication credentials were not provided."}` |
| `403` | User is not a superuser | `{"detail": "You do not have permission to perform this action."}` |

---

### Create Subcategory

| | |
|---|---|
| Endpoint | `POST /dashboard/subcategories/` |
| Auth Required | Yes (Superuser) |
| Content-Type | `multipart/form-data` |

#### Request Body (Form Data)

```
category: 5 (required)
name_en: "Phones" (required)
name_ar: "هواتف" (required)
image: <file> (optional)
```

#### Field Requirements

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | integer | Yes | Parent category ID |
| `name_en` | string | Yes | Subcategory name in English (only English letters and spaces) |
| `name_ar` | string | Yes | Subcategory name in Arabic (only Arabic letters and spaces) |
| `image` | file | No | Subcategory image (uploaded to Cloudinary, returns image_url) |

#### Response

Status: `201 Created`

```json
{ "id": 12, "name_en": "Phones", "name_ar": "هواتف", "category": 5, "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/subcategory.jpg" }
```

**Note:** If no image is uploaded, `image_url` will be an empty string `""`.

#### Errors

| Status | Description | Response Example |
|--------|-------------|------------------|
| `400` | Validation error (empty/invalid names) | `{"name_en": ["This field may not be blank."]}` |
| `400` | Category does not exist | `{"category": ["Invalid pk \"999\" - object does not exist."]}` |
| `400` | Duplicate subcategory under the same category | `{"name_en": ["Subcategory already exists for this category."]}` or `{"name_ar": ["Subcategory already exists for this category."]}` |
| `401` | Missing or invalid authentication token | `{"detail": "Authentication credentials were not provided."}` |
| `403` | User is not a superuser | `{"detail": "You do not have permission to perform this action."}` |

---

##  Ad Request Management

### List All Ad Requests

| | |
|---|---|
| Endpoint | `GET /dashboard/ads/` |
| Auth Required | Yes (Superuser) |
| Request Body | None |

#### Response

Status: `200 OK`

```json
{
  "count": 12,
  "next": "http://localhost:8000/dashboard/ads/?page=2",
  "previous": null,
  "results": [
    {
      "id": 15,
      "user": { "id": 12, "phone": "96812345678", "full_name_ar": "محمد أحمد", "full_name_en": "Mohammed Ahmed" },
      "product": { "id": 45, "name_en": "Dell Laptop", "name_ar": "حاسوب ديل" },
      "duration_preference": "30 days",
      "requested_at": "2025-10-08T14:20:00Z",
      "status": "pending",
      "approved_by": null,
      "approved_at": null
    }
  ]
}
```

---

### Approve Ad Request

| | |
|---|---|
| Endpoint | `PATCH /dashboard/ads/{id}/approve/` |
| Auth Required | Yes (Superuser) |
| Content-Type | `application/json` |

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | Ad request ID to approve |

#### Request Body (Choose One Option)

Option 1: Duration in Days
```json
{ "duration_days": 30 }
```

Option 2: Specific Dates
```json
{ "ad_start": "2025-10-09T00:00:00", "ad_end": "2025-11-09T00:00:00" }
```

#### Response

Status: `200 OK`

```json
{ "message": "Product 'حاسوب ديل' marked as Ad from 2025-10-09 to 2025-11-09." }
```

#### Errors

| Status | Description | Response Example |
|--------|-------------|------------------|
| `400` | Missing duration or invalid data | `{"error": "Provide duration_days or ad_end"}` |
| `400` | Invalid duration value | `{"error": "duration_days must be an integer"}` |
| `401` | Missing or invalid authentication token | `{"detail": "Authentication credentials were not provided."}` |
| `403` | User is not a superuser | `{"detail": "You do not have permission to perform this action."}` |
| `404` | Ad request not found | `{"detail": "Not found."}` |
| `409` | Ad request already approved (cannot modify) | `{"error": "Ad request is already approved and cannot be modified.", "product": 45, "ad_start": "2025-10-09T00:00:00Z", "ad_end": "2025-11-09T00:00:00Z"}` |

---

##  User Management

### List All Users

| | |
|---|---|
| Endpoint | `GET /dashboard/users/` |
| Auth Required | Yes (Superuser) |
| Request Body | None |

#### Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `search` | string | No | Search in phone, email, names, governorate, wilayat | `?search=Mohammed` |
| `ordering` | string | No | Sort: `date_joined`, `-date_joined`, `email`, `-email`, `phone`, `-phone` | `?ordering=-date_joined` |

#### Response

**Status**: `200 OK`

```json
{
  "count": 245,
  "next": "http://localhost:8000/dashboard/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 12,
      "phone": "96812345678",
      "email": "mohammed@example.com",
      "full_name_ar": "محمد أحمد",
      "full_name_en": "Mohammed Ahmed",
      "governorate": "Muscat",
      "wilayat": "Muscat",
      "is_active": true,
      "is_staff": false,
      "is_superuser": false,
      "date_joined": "2025-09-15T10:30:00Z",
      "extra_monthly_posts": 0
    }
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | User ID |
| `phone` | string | Phone number (unique) |
| `email` | string | Email address |
| `full_name_ar` | string | Full name in Arabic |
| `full_name_en` | string | Full name in English |
| `governorate` | string | User's governorate |
| `wilayat` | string | User's wilayat |
| `is_active` | boolean | Account is active |
| `is_staff` | boolean | Has staff privileges |
| `is_superuser` | boolean | Has superuser privileges |
| `date_joined` | datetime | Account creation date |
| `extra_monthly_posts` | integer | Additional free posts for current month |

#### Errors

| Status | Description |
|--------|-------------|
| `401` | Missing or invalid authentication token |
| `403` | User is not a superuser |

---

### Get User Details

| | |
|---|---|
| Endpoint | `GET /dashboard/users/{id}/` |
| Auth Required | Yes (Superuser) |
| Request Body | None |

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | User ID |

#### Response

**Status**: `200 OK`

```json
{
  "id": 12,
  "phone": "96812345678",
  "email": "mohammed@example.com",
  "full_name_ar": "محمد أحمد",
  "full_name_en": "Mohammed Ahmed",
  "governorate": "Muscat",
  "wilayat": "Muscat",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "date_joined": "2025-09-15T10:30:00Z",
  "last_login": "2025-10-09T09:45:00Z",
  "extra_monthly_posts": 0
}
```

#### Additional Fields (vs List)

| Field | Type | Description |
|-------|------|-------------|
| `last_login` | datetime/null | Last login timestamp |

#### Errors

| Status | Description |
|--------|-------------|
| `401` | Missing or invalid authentication token |
| `403` | User is not a superuser |
| `404` | User not found |

---

### Update User

| | |
|---|---|
| Endpoint | `PATCH /dashboard/users/{id}/` |
| Auth Required | Yes (Superuser) |
| Content-Type | `application/json` |

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | User ID to update |

#### Request Body (All Fields Optional)

```json
{
  "email": "newemail@example.com",
  "full_name_ar": "محمد أحمد السعيد",
  "full_name_en": "Mohammed Ahmed Al Saeed",
  "governorate": "Muscat",
  "wilayat": "Bausher",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "extra_monthly_posts": 10
}
```

#### Updatable Fields

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `email` | string | Email address | Must be valid email format |
| `full_name_ar` | string | Full name in Arabic | Only Arabic characters |
| `full_name_en` | string | Full name in English | Only English characters |
| `governorate` | string | User's governorate | Must be valid governorate |
| `wilayat` | string | User's wilayat | Must be valid for the governorate |
| `is_active` | boolean | Account active status | true/false |
| `is_staff` | boolean | Staff privileges | true/false |
| `is_superuser` | boolean | Superuser privileges | true/false |
| `extra_monthly_posts` | integer | Extra free posts | Non-negative integer |

#### Response

**Status**: `200 OK`

```json
{
  "id": 12,
  "phone": "96812345678",
  "email": "newemail@example.com",
  "full_name_ar": "محمد أحمد السعيد",
  "full_name_en": "Mohammed Ahmed Al Saeed",
  "governorate": "Muscat",
  "wilayat": "Bausher",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "date_joined": "2025-09-15T10:30:00Z",
  "last_login": "2025-10-09T09:45:00Z",
  "extra_monthly_posts": 10
}
```

#### Errors

| Status | Description | Response Example |
|--------|-------------|------------------|
| `400` | Validation error | `{"email": ["Enter a valid email address."]}` |
| `400` | Invalid wilayat for governorate | `{"wilayat": ["Bausher is not valid for Dhofar"]}` |
| `401` | Missing or invalid authentication token | `{"detail": "Authentication credentials were not provided."}` |
| `403` | User is not a superuser | `{"detail": "You do not have permission to perform this action."}` |
| `404` | User not found | `{"detail": "Not found."}` |

---

### Delete User

| | |
|---|---|
| Endpoint | `DELETE /dashboard/users/{id}/` |
| Auth Required | Yes (Superuser) |
| Request Body | None |

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | User ID to delete |

#### Response

**Status**: `204 No Content`

No response body returned on success.

#### Errors

| Status | Description | Response Example |
|--------|-------------|------------------|
| `401` | Missing or invalid authentication token | `{"detail": "Authentication credentials were not provided."}` |
| `403` | User is not a superuser | `{"detail": "You do not have permission to perform this action."}` |
| `403` | Attempting to delete a superuser | `{"error": "Cannot delete a superuser account"}` |
| `404` | User not found | `{"detail": "Not found."}` |

---
