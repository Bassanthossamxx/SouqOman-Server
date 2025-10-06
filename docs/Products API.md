# Products API Documentation

**Base URL:** `/api/`

**Authentication:** JWT (Authorization: `Bearer <token>`)

---

## Table of Contents
1. [Authentication & Permissions](#authentication--permissions)
2. [Category Endpoints](#category-endpoints)
3. [SubCategory Endpoints](#subcategory-endpoints)
4. [Product Endpoints](#product-endpoints)
5. [Error Responses](#error-responses)

---

## Authentication & Permissions

- **Authentication Method:** JWT tokens via Authorization header
- **Header Format:** `Authorization: Bearer <access_token>`
- **Permissions:**
  - **Categories & Subcategories:** 
    - Read (GET): Public access
    - Write (POST/DELETE): Superuser only
  - **Products:**
    - List (GET /products/): Public access
    - Create (POST /products/): Authenticated users only
    - Retrieve (GET /products/{id}/): Public access

---

## Category Endpoints

### 1. List All Categories
**Endpoint:** `GET /api/categories/`

**Description:** Retrieve all categories without subcategories.

**Permissions:** Public

**Response (200 OK):**
```json
{
    "id": 1,
    "name_en": "Electronics",
    "name_ar": "إلكترونيات"
}
```

---

### 2. Create Category
**Endpoint:** `POST /api/categories/`

**Description:** Create a new category.

**Permissions:** Superuser only

**Request Body:**
```json
{
  "name_en": "Electronics",
  "name_ar": "إلكترونيات"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "name_en": "Electronics",
  "name_ar": "إلكترونيات"
}
```

**Validation Rules:**
- `name_en` and `name_ar` must be unique across all categories
- Both fields are required

**Error Response (400 Bad Request):**
```json
{
  "name_ar": ["category with this name ar already exists."],
  "name_en": ["category with this name en already exists."]
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 3. Retrieve Category Details
**Endpoint:** `GET /api/categories/{id}/`

**Description:** Retrieve a single category with all its subcategories.

**Permissions:** Public

**Response (200 OK):**
```json
{
  "id": 1,
  "name_en": "Electronics",
  "name_ar": "إلكترونيات",
  "subcategories": [
    {
      "id": 10,
      "name_en": "Phones",
      "name_ar": "هواتف",
      "category": 1
    },
    {
      "id": 11,
      "name_en": "Laptops",
      "name_ar": "حاسبات",
      "category": 1
    }
  ]
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 4. Delete Category
**Endpoint:** `DELETE /api/categories/{id}/`

**Description:** Delete a category.

**Permissions:** Superuser only

**Response (204 No Content):** Empty body

**Error Responses:**
- **404 Not Found:** Category doesn't exist
- **403 Forbidden:** Not a superuser

---

## SubCategory Endpoints

### 1. List All SubCategories
**Endpoint:** `GET /api/subcategories/`

**Description:** Retrieve all subcategories across all categories.

**Permissions:** Public

**Response (200 OK):**
```json
{
  "id": 10,
  "name_en": "Phones",
  "name_ar": "هواتف",
  "category": 1
},
{
  "id": 11,
  "name_en": "Laptops",
  "name_ar": "حاسبات",
  "category": 1
}
```

---

### 2. Create SubCategory
**Endpoint:** `POST /api/subcategories/`

**Description:** Create a new subcategory under a category.

**Permissions:** Superuser only

**Request Body:**
```json
{
  "name_en": "Tablets",
  "name_ar": "أجهزة لوحية",
  "category": 1
}
```

**Response (201 Created):**
```json
{
  "id": 12,
  "name_en": "Tablets",
  "name_ar": "أجهزة لوحية",
  "category": 1
}
```

**Validation Rules:**
- Required fields: `name_en`, `name_ar`, `category`
- Unique together: (`category`, `name_en`) and (`category`, `name_ar`)

**Error Response (400 Bad Request):**
```json
{
  "non_field_errors": ["The fields category, name_en must make a unique set."]
}
```

---

## Product Endpoints

### 1. List All Products (with Filtering & Sorting)
**Endpoint:** `GET /api/products/`

**Description:** Retrieve all products with support for filtering, searching, and sorting.

**Permissions:** Public

| Parameter             | Type    | Description                                                        | Example                           |
|-----------------------|---------|--------------------------------------------------------------------|-----------------------------------|
| `search`              | string  | Search across product names and category/subcategory names (AR/EN)  | `search=هاتف`                     |
| `category__name_en`   | string  | Filter by category English name                                    | `category__name_en=Electronics`   |
| `category__name_ar`   | string  | Filter by category Arabic name                                     | `category__name_ar=إلكترونيات`    |
| `subcategory__name_en`| string  | Filter by subcategory English name                                 | `subcategory__name_en=Phones`     |
| `subcategory__name_ar`| string  | Filter by subcategory Arabic name                                  | `subcategory__name_ar=هواتف`      |
| `price`               | decimal | Filter by exact price                                              | `price=350.00`                    |
| `governorate`         | string  | Filter by governorate                                              | `governorate=Muscat`              |
| `wilayat`             | string  | Filter by wilayat                                                  | `wilayat=Muscat`                  |
| `ordering`            | string  | Sort results                                                       | See sorting options below          |
**Sorting Options (ordering parameter):**
- `price` - Price low to high
- `-price` - Price high to low
- `posted_at` - Oldest first
- `-posted_at` - Newest first (default)
- `views_count` - Least viewed first
- `-views_count` - Most viewed first

**Example Requests:**
```
GET /api/products/
GET /api/products/?search=هاتف
GET /api/products/?category__name_ar=إلكترونيات&ordering=-price
GET /api/products/?governorate=Muscat&wilayat=Muscat&ordering=-views_count
GET /api/products/?search=phone&ordering=price
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_full_name_en": "Ahmed Al Balushi",
  "user_full_name_ar": "أحمد البلوشي",
  "category_name_en": "Electronics",
  "category_name_ar": "إلكترونيات",
  "subcategory_name_en": "Phones",
  "subcategory_name_ar": "هواتف",
  "name_en": "iPhone 14",
  "name_ar": "آيفون 14",
  "governorate": "Muscat",
  "wilayat": "Muscat",
  "image_urls": [
    { "id": 101, "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file.jpg" }
  ],
  "price": "350.00",
  "description": "Brand new iPhone 14 with warranty.",
  "contact_phone": "+96891234567",
  "whatsapp_url": "https://wa.me/96891234567"
}
```

---

### 2. Create Product
**Endpoint:** `POST /api/products/`

**Description:** Create a new product listing.

**Permissions:** Authenticated users only

**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
```
category: 1
subcategory: 10 (optional)
name_en: "iPhone 14" (optional)
name_ar: "آيفون 14" (required)
governorate: "Muscat" (required)
wilayat: "Muscat" (required)
price: 350.00 (required)
description: "Brand new iPhone 14." (required)
contact_phone: "+96891234567" (required)
images: [<file1>, <file2>, ...] (required, up to 5)
```

**Field Requirements:**
- **Required:** `name_ar`, `category`, `governorate`, `wilayat`, `price`, `description`, `contact_phone`, `images`
- **Optional:** `name_en`, `subcategory`
- **Images:** Up to 5 images will be saved; if more than 5 are uploaded, only the first 5 are stored
- **Phone Format:** Must be Omani format `+968XXXXXXXX`

**Response (201 Created):**
```json
{
  "id": 1,
  "user_full_name_en": "Ahmed Al Balushi",
  "user_full_name_ar": "أحمد البلوشي",
  "category_name_en": "Electronics",
  "category_name_ar": "إلكترونيات",
  "subcategory_name_en": "Phones",
  "subcategory_name_ar": "هواتف",
  "name_en": "iPhone 14",
  "name_ar": "آيفون 14",
  "governorate": "Muscat",
  "wilayat": "Muscat",
  "image_urls": [
    { "id": 101, "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file.jpg" }
  ],
  "price": "350.00",
  "description": "Brand new iPhone 14.",
  "contact_phone": "+96891234567",
  "whatsapp_url": "https://wa.me/96891234567"
}
```

**Validation Errors (400 Bad Request):**
```json
{
  "subcategory": ["This subcategory does not belong to the selected category."]
}
```
```json
{
  "wilayat": ["Wilayat 'Muttrah' is not valid for governorate 'Muscat'."]
}
```
```json
{
  "images": ["At least one image is required."]
}
```
```json
{
  "price": ["Price must be at least 10.00."]
}
```
```json
{
  "contact_phone": ["Phone must follow Omani format: +968XXXXXXXX"]
}
```

**Authentication Error (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### 3. Retrieve Product Details
**Endpoint:** `GET /api/products/{id}/`

**Description:** Retrieve full product details. **Note:** Views count is automatically incremented with each request.

**Permissions:** Public

**Response (200 OK):**
```json
{
  "id": 1,
  "user_full_name_en": "Ahmed Al Balushi",
  "user_full_name_ar": "أحمد البلوشي",
  "category_name_en": "Electronics",
  "category_name_ar": "إلكترونيات",
  "subcategory_name_en": "Phones",
  "subcategory_name_ar": "هواتف",
  "name_en": "iPhone 14",
  "name_ar": "آيفون 14",
  "governorate": "Muscat",
  "wilayat": "Muscat",
  "image_urls": [
    { "id": 101, "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file.jpg" }
  ],
  "price": "350.00",
  "description": "Brand new iPhone 14 with warranty.",
  "contact_phone": "+96891234567",
  "whatsapp_url": "https://wa.me/96891234567"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

## Error Responses

### Standard Error Format
All validation errors follow Django REST Framework's standard format:

```json
{
  "field_name": ["Error message for this field."],
  "another_field": ["Another error message."]
}
```

### Common HTTP Status Codes

| Code | Meaning | When It Occurs |
|------|---------|----------------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST request |
| 204 | No Content | Successful DELETE request |
| 400 | Bad Request | Validation errors, malformed data |
| 401 | Unauthorized | Missing or invalid authentication credentials |
| 403 | Forbidden | Authenticated but lacking permissions |
| 404 | Not Found | Resource doesn't exist |

---

## Notes & Best Practices

1. **Views Count:** The `views_count` field is automatically incremented each time a product detail is accessed via `GET /api/products/{id}/`. You don't need to manually update it.

2. **Image Upload (Cloudinary):** Images are uploaded to Cloudinary. Each product stores up to 5 images as a list of objects with `id` and `url` (secure URL). If you upload more than 5 images, only the first 5 are saved.

3. **Phone Number:** Contact phone must be in Omani format (`+968XXXXXXXX`). The WhatsApp URL is automatically generated from this number.

4. **Governorate/Wilayat Validation:** The system validates that the wilayat belongs to the selected governorate. Invalid combinations will be rejected.

5. **Subcategory Validation:** If a subcategory is provided, it must belong to the selected category.

6. **Search Functionality:** The search parameter searches across:
   - Product names (Arabic and English)
   - Category names (Arabic and English)
   - Subcategory names (Arabic and English)

7. **Multiple Filters:** You can combine multiple query parameters for complex filtering:
   ```
   GET /api/products/?category__name_ar=إلكترونيات&governorate=Muscat&ordering=-price
   ```

8. **Configuration:** Cloudinary is configured via the `CLOUDINARY_URL` environment variable (see README). Secure URLs are returned by default.

---

## Future Enhancements (Planned)

- **Ad System:** Promote products as featured ads
- **Update/Delete Products:** PATCH and DELETE endpoints for product owners
- **Advanced Filtering:** Price range filters, date range filters
- **Pagination:** For large product lists
- **Favorites/Bookmarks:** User-specific product collections
