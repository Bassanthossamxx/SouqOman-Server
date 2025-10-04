# Products API (Current + Next Steps)

Base URL prefix: `/api/`

Auth & permissions
- Authentication: JWT (Authorization: `Bearer <token>`). See auth docs for obtaining tokens.
- Permission on products app endpoints: Read (GET/HEAD/OPTIONS) is public; write (POST/DELETE) requires superuser.

---

## Category Endpoints

### GET /api/categories/
List all categories (no subcategories embedded).

Response 200 (application/json)
[
  {
    "id": 1,
    "name_en": "Electronics",
    "name_ar": "إلكترونيات"
  }
]

---

### POST /api/categories/  (superuser)
Create a new category.

Request body (application/json)
{
  "name_en": "Electronics",
  "name_ar": "إلكترونيات"
}

Response 201
{
  "id": 3,
  "name_en": "Electronics",
  "name_ar": "إلكترونيات"
}

Validation/Errors
- Unique on both `name_en` and `name_ar` across all categories.
- 400 if unique/required validation fails.
- 403 if not superuser.

---

### GET /api/categories/{id}/
Retrieve a single category including its subcategories.

Response 200
{
  "id": 1,
  "name_en": "Electronics",
  "name_ar": "إلكترونيات",
  "subcategories": [
    { "id": 10, "name_en": "Phones", "name_ar": "هواتف", "category": 1 },
    { "id": 11, "name_en": "Laptops", "name_ar": "حاسبات", "category": 1 }
  ]
}

Errors
- 404 if not found.

---

### DELETE /api/categories/{id}/  (superuser)
Delete a category.

Response 204 No Content

Errors
- 404 if not found.
- 403 if not superuser.
- 400/409 possible at database level if foreign key constraints are violated (e.g., dependent subcategories). Behavior depends on DB and constraint handling.

---

## SubCategory Endpoints

### GET /api/subcategories/
List all subcategories.

Response 200
[
  { "id": 10, "name_en": "Phones",  "name_ar": "هواتف",  "category": 1 },
  { "id": 11, "name_en": "Laptops", "name_ar": "حاسبات", "category": 1 }
]

---

### POST /api/subcategories/  (superuser)
Create a new subcategory.

Request body (application/json)
{
  "name_en": "Tablets",
  "name_ar": "أجهزة لوحية",
  "category": 1
}

Response 201
{
  "id": 12,
  "name_en": "Tablets",
  "name_ar": "أجهزة لوحية",
  "category": 1
}

Validation/Errors
- Required: `name_en`, `name_ar`, `category`.
- Uniqueness: (`category`, `name_en`) and (`category`, `name_ar`) must be unique together.
- 400 for validation errors, 403 if not superuser.

---

## Error Response Example (validation)

Response 400
{
  "name_ar": ["This field must be unique."],
  "name_en": ["This field must be unique."]
}

---

## What’s Not Implemented Yet (from Products & Home Overview)
The overview describes PRODUCT, AD, search/filter/sort, and response shaping that are not yet present in code. Below is the proposed API and a concrete to‑do plan to deliver it.

### Proposed Models
- Product
  - Fields (per overview): product_id (id), name_en (optional), name_ar (required), governorate (required), wilayat (required), price (>= 0), description (required), posted_at (auto), views_count (auto/increment), contact_phone (required, WhatsApp format `+968XXXXXXXX`), category (FK), subcategory (FK, optional), cover_image, other_images (0–7).
  - Validation rules:
    - Ensure subcategory belongs to the same category.
    - Validate governorate/wilayat pair against allowed list.
    - Validate phone format and provide normalized value (e.g., strip `+`).
    - Enforce max 7 additional images; exactly one cover image.
- Ad (one-to-one with Product)
  - Fields: is_active (bool), start_date (required if active), duration_days (int) with expiry logic.

### Proposed Endpoints
- Products
  - GET /api/products/
    - Query params: `search`, `category_id`, `subcategory_id`, `price_min`, `price_max`, `governorate`, `wilayat`, `ordering` in {`-posted_at` (default), `posted_at`, `price`, `-price`}.
    - Response includes computed: `is_ad`, `whatsapp_link`, separate `cover_image` vs `other_images`.
  - POST /api/products/  (auth required; define role policy)
    - Create product with images upload support.
  - GET /api/products/{id}/
    - Returns full product record, increments `views_count`.
  - PATCH /api/products/{id}/  (owner/admin)
  - DELETE /api/products/{id}/  (owner/admin)
- Ads
  - POST /api/products/{id}/ad/activate  (admin or paid flow)
    - Body: `{ "start_date": "2025-09-14T10:22:11Z", "duration_days": 7 }`.
  - POST /api/products/{id}/ad/deactivate
  - Optional: GET /api/ads/ for admin reporting.

### Serializer/Response Rules
- Product list item
  {
    "product_id": 51,
    "name_ar": "ايفون 15 برو",
    "name_en": "iPhone 15 Pro",
    "price": 450.0,
    "cover_image": "https://cdn.ex.com/51/cover.jpg",
    "other_images": ["https://cdn.ex.com/51/1.jpg", "https://cdn.ex.com/51/2.jpg"],
    "governorate": "Muscat",
    "wilayat": "Al Seeb",
    "views_count": 129,
    "posted_at": "2025-09-14T10:22:11Z",
    "contact_phone": "+96891234567",
    "whatsapp_link": "https://wa.me/96891234567",
    "category_id": 3,
    "subcategory_id": 12,
    "is_ad": true
  }

### Filtering & Search Contract
- `search`: text across `name_ar`, `name_en`.
- Filters: `category_id`, `subcategory_id`, `price_min`, `price_max`, `governorate`, `wilayat`.
- Sorting: `ordering` param as above.

### To‑Do Checklist (Next Steps)
1) Models & migrations
   - [ ] Create `Product` model with fields/constraints above.
   - [ ] Create `Ad` model (OneToOne to Product) with activation/expiry logic.
   - [ ] Add image handling: `images_urls` (will use cloudinary).
   - [ ] Add choices/validation lists for `governorate` and `wilayat` (reuse central choices). Ensure pair validity.
   - [ ] Add phone validator to enforce `+968XXXXXXXX` and normalize for `whatsapp_link`.
   - [ ] Auto set `posted_at`; maintain `views_count` efficiently (consider F expressions).

2) Serializers
   - [ ] `ProductSerializer` (create/update) with validations: price >= 0, subcategory matches category, images limit.
   - [ ] `ProductListSerializer` (list) exposing required response fields and `whatsapp_link`, `is_ad`.
   - [ ] `AdSerializer` for admin actions.

3) Views & URLs
   - [ ] List/Create: `GET/POST /api/products/` with search, filters, ordering.
   - [ ] Retrieve/Update/Delete: `GET/PATCH/DELETE /api/products/{id}/` (increment `views_count` on GET).
   - [ ] Ad activation endpoints: `POST /api/products/{id}/ad/activate`, `POST /api/products/{id}/ad/deactivate`.
   - [ ] Register routes in `apps.products.urls`.
   - [ ] Add search and filter and sort endpoints too
   - 
   


4) Docs & schema
   - [ ] Update this doc once endpoints are added.
   - [ ] Update postman collection.


---

