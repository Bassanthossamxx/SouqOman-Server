# Products API Documentation - User Endpoints

**Base URL:** `/api/`

**Authentication:** JWT (Authorization: `Bearer <token>`)

---

## Table of Contents
1. [Authentication & Permissions](#authentication--permissions)
2. [Pagination](#pagination)
3. [Category Endpoints](#category-endpoints)
4. [SubCategory Endpoints](#subcategory-endpoints)
5. [Product Endpoints](#product-endpoints)
6. [Ad Request Endpoints](#ad-request-endpoints)
7. [Data Reference](#data-reference)

---

## Authentication & Permissions

- **Authentication Method:** JWT tokens via Authorization header
- **Header Format:** `Authorization: Bearer <access_token>`
- **Permissions:**
  - **Categories & Subcategories:**
    - Read (GET): Public access
  - **Products:**
    - List (GET): Public access
    - Create (POST): Authenticated users only
    - Retrieve (GET): Public access
    - Update (PUT/PATCH): Owner only
    - Delete (DELETE): Owner only (soft delete)
  - **Ad Requests:**
    - Create (POST): Authenticated users only

---

## Pagination

- All list endpoints are paginated with a fixed page size of 20 items per page.
- Use the `page` query parameter to navigate pages (1-indexed).
- Response shape for paginated endpoints:
```
{
  "count": <total_items>,
  "next": "<url or null>",
  "previous": "<url or null>",
  "results": [ ...items... ]
}
```

---

## Category Endpoints

### 1. List All Categories
**Endpoint:** `GET /api/categories/`

**Description:** Retrieve all categories without subcategories.

**Permissions:** Public

**Request Headers:**
```
(No authentication required)
```

**Query Parameters:**
- `page` (integer, optional) — Page number (default: 1)

**Response (200 OK):**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    { "id": 1, "name_en": "Electronics", "name_ar": "إلكترونيات", "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/category1.jpg" },
    { "id": 2, "name_en": "Fashion", "name_ar": "أزياء", "image_url": "" },
    { "id": 3, "name_en": "Vehicles", "name_ar": "مركبات", "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/category3.jpg" }
  ]
}
```

**Response for Empty Database (200 OK):**
```json
{ "count": 0, "next": null, "previous": null, "results": [] }
```

---

### 2. Retrieve Category Details
**Endpoint:** `GET /api/categories/{id}/`

**Description:** Retrieve a single category with all its subcategories.

**Permissions:** Public

**Request Headers:**
```
(No authentication required)
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name_en": "Electronics",
  "name_ar": "إلكترونيات",
  "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/category1.jpg",
  "subcategories": [
    { "id": 10, "name_en": "Phones", "name_ar": "هواتف", "category": 1, "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/subcat1.jpg" },
    { "id": 11, "name_en": "Laptops", "name_ar": "لابتوبات", "category": 1, "image_url": "" }
  ]
}
```

**Response (200 OK) - Category with no subcategories:**
```json
{ "id": 2, "name_en": "Fashion", "name_ar": "أزياء", "image_url": "", "subcategories": [] }
```

**Error Response (404 Not Found):**
```json
{ "detail": "Not found." }
```

---

## SubCategory Endpoints

### 1. List All SubCategories
**Endpoint:** `GET /api/subcategories/`

**Description:** Retrieve all subcategories across all categories.

**Permissions:** Public

**Request Headers:**
```
(No authentication required)
```

**Query Parameters:**
- `page` (integer, optional) — Page number (default: 1)

**Response (200 OK):**
```json
{
  "count": 12,
  "next": "http://localhost:8000/api/subcategories/?page=2",
  "previous": null,
  "results": [
    { "id": 10, "name_en": "Phones", "name_ar": "هواتف", "category": 1, "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/subcat1.jpg" },
    { "id": 11, "name_en": "Laptops", "name_ar": "لابتوبات", "category": 1, "image_url": "" },
    { "id": 12, "name_en": "Dresses", "name_ar": "فساتين", "category": 2, "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v123/subcat2.jpg" }
  ]
}
```

**Response for Empty Database (200 OK):**
```json
{ "count": 0, "next": null, "previous": null, "results": [] }
```

---

## Product Endpoints

### 1. List All Products (with Filtering, Searching, Sorting)
**Endpoint:** `GET /api/products/`

**Description:** Retrieve all active products with support for bilingual filtering (EN/AR), searching, and sorting. Only active products are shown to normal users.

**Permissions:** Public (no authentication required)

**Request Headers:**
```
(No authentication required)
```

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `page` | integer | Page number (1-indexed). 20 items per page | `?page=2` |
| `search` | string | Free-text search across product names and category/subcategory names (AR/EN) | `?search=هاتف` |
| `category` | string | Filter by category name (AR or EN, partial, case-insensitive) | `?category=إلكترونيات` |
| `subcategory` | string | Filter by subcategory name (AR or EN, partial, case-insensitive) | `?subcategory=هواتف` |
| `min_price` | number | Minimum price (inclusive) | `?min_price=50` |
| `max_price` | number | Maximum price (inclusive) | `?max_price=500` |
| `governorate` | string | Bilingual filter. Accepts EN or AR, supports partial match | `?governorate=مسقط` or `?governorate=Muscat` |
| `wilayat` | string | Bilingual filter. Accepts EN or AR, supports partial match | `?wilayat=مطرح` or `?wilayat=Muttrah` |
| `ordering` | string | Sorting field. One of: `price`, `-price`, `posted_at`, `-posted_at`, `views_count`, `-views_count` | `?ordering=-price` |

**Ordering Options:**
- `price`: Price low to high
- `-price`: Price high to low (descending)
- `posted_at`: Oldest first
- `-posted_at`: Newest first (default)
- `views_count`: Least viewed first
- `-views_count`: Most viewed first

**Examples:**
- `GET /api/products/` - All products (default ordering: newest first)
- `GET /api/products/?search=هاتف` - Search for "هاتف" in all text fields
- `GET /api/products/?category=إلكترونيات&ordering=-price` - Electronics sorted by price (high to low)
- `GET /api/products/?subcategory=هواتف&min_price=50&max_price=500` - Phones between 50-500
- `GET /api/products/?governorate=مسقط` - Products in Muscat governorate
- `GET /api/products/?wilayat=مطرح` - Products in Muttrah wilayat
- `GET /api/products/?governorate=Muscat&wilayat=Muttrah&ordering=-views_count` - Most viewed in Muscat/Muttrah
- `GET /api/products/?min_price=100&max_price=1000&ordering=price` - Products 100-1000, cheapest first

**Response (200 OK):**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user_full_name_en": "Ahmed Al Balushi",
      "user_full_name_ar": "أحمد البلوشي",
      "category": 1,
      "category_name_en": "Electronics",
      "category_name_ar": "إلكترونيات",
      "subcategory": 10,
      "subcategory_name_en": "Phones",
      "subcategory_name_ar": "هواتف",
      "name_en": "iPhone 14",
      "name_ar": "آيفون 14",
      "governorate": "Muscat",
      "wilayat": "Muscat",
      "price": "350.00",
      "description": "Brand new iPhone 14 with warranty.",
      "contact_phone": "+96891234567",
      "whatsapp_url": "https://wa.me/96891234567",
      "image_urls": [ { "url": "https://res.cloudinary.com/your-cloud/image/upload/v123/file.jpg" } ],
      "status": "active",
      "ad": false,
      "posted_at": "2025-10-09T12:34:56Z"
    },
    {
      "id": 2,
      "user_full_name_en": "Fatima Al Lawati",
      "user_full_name_ar": "فاطمة اللواتي",
      "category": 1,
      "category_name_en": "Electronics",
      "category_name_ar": "إلكترونيات",
      "subcategory": null,
      "subcategory_name_en": null,
      "subcategory_name_ar": null,
      "name_en": null,
      "name_ar": "كمبيوتر محمول",
      "governorate": "Dhofar",
      "wilayat": "Salalah",
      "price": "500.00",
      "description": "Used laptop in good condition.",
      "contact_phone": "+96898765432",
      "whatsapp_url": "https://wa.me/96898765432",
      "image_urls": [
        { "url": "https://res.cloudinary.com/your-cloud/image/upload/v123/file1.jpg" },
        { "url": "https://res.cloudinary.com/your-cloud/image/upload/v123/file2.jpg" }
      ],
      "status": "active",
      "ad": true,
      "posted_at": "2025-10-08T10:20:30Z"
    }
  ]
}
```

**Response for Empty Results (200 OK):**
```json
{ "count": 0, "next": null, "previous": null, "results": [] }
```

---

### 2. Create Product
**Endpoint:** `POST /api/products/`

**Description:** Create a new product listing. The authenticated user will be automatically set as the product owner. Users have a monthly quota (default: 4 free products per month). If the quota is exceeded, the product will be pending approval.

**Permissions:** Authenticated users only

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body:**
```
category: 1 (required)
subcategory: 10 (optional, can be null/omitted)
name_en: "iPhone 14" (optional, if user doesn't provide, it will translate from Arabic)
name_ar: "آيفون 14" (required)
governorate: "Muscat" (required)
wilayat: "Muscat" (required)
price: 350.00 (required)
description: "Brand new iPhone 14." (required)
contact_phone: "+96891234567" (required)
images: [<file1>, <file2>, ...] (required, 1-5 files)
```
#### Note: if user doesn't enter english name, it will be auto-translated from arabic to english.

**Field Requirements:**

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `category` | integer | Yes | Must be valid category ID | - |
| `subcategory` | integer | No | Must belong to selected category | Can be null/omitted |
| `name_en` | string | No | Only English letters and spaces | optional but if not added will translate arabic name to english|
| `name_ar` | string | Yes | Only Arabic letters and spaces | - |
| `governorate` | string | Yes | Must be valid governorate key (EN) | See [Governorate Options](#governorate-options) |
| `wilayat` | string | Yes | Must be valid wilayat for selected governorate | See [Wilayat Options](#wilayat-options) |
| `price` | decimal | Yes | Minimum 10.00 | Max 10 digits, 2 decimal places |
| `description` | text | Yes | - | No length limit |
| `contact_phone` | string | Yes | Egyptian (+20XXXXXXXXXX) or Omani (+968XXXXXXXX) format | Egyptian: 10 digits after +20, Omani: 8 digits after +968 |
| `images` | files | Yes | 1-5 image files | Maximum 5 images allowed |

**Response (201 Created) - Within Quota:**
```json
{
  "id": 1,
  "user_full_name_en": "Ahmed Al Balushi",
  "user_full_name_ar": "أحمد البلوشي",
  "category": 1,
  "category_name_en": "Electronics",
  "category_name_ar": "إلكترونيات",
  "subcategory": 10,
  "subcategory_name_en": "Phones",
  "subcategory_name_ar": "هواتف",
  "name_en": "iPhone 14",
  "name_ar": "آيفون 14",
  "governorate": "Muscat",
  "wilayat": "Muscat",
  "price": "350.00",
  "description": "Brand new iPhone 14.",
  "contact_phone": "+96891234567",
  "whatsapp_url": "https://wa.me/96891234567",
  "image_urls": [
    { "url": "https://res.cloudinary.com/your-cloud/image/upload/v123/file.jpg" }
  ],
  "status": "active",
  "ad": false,
  "posted_at": "2025-10-09T12:34:56Z"
}
```

**Response (201 Created) - Quota Exceeded (Pending Approval):**
```json
{
  "id": 5,
  "user_full_name_en": "Ahmed Al Balushi",
  "user_full_name_ar": "أحمد البلوشي",
  "category": 1,
  "category_name_en": "Electronics",
  "category_name_ar": "إلكترونيات",
  "subcategory": 10,
  "subcategory_name_en": "Phones",
  "subcategory_name_ar": "هواتف",
  "name_en": "Samsung Galaxy",
  "name_ar": "سامسونج جالاكسي",
  "governorate": "Muscat",
  "wilayat": "Muscat",
  "price": "250.00",
  "description": "Brand new Samsung Galaxy.",
  "contact_phone": "+96891234567",
  "whatsapp_url": "https://wa.me/96891234567",
  "image_urls": [
    { "url": "https://res.cloudinary.com/your-cloud/image/upload/v123/file.jpg" }
  ],
  "status": "pending",
  "ad": false,
  "posted_at": "2025-10-09T12:34:56Z",
  "message": "You have reached your free posting limit this month. Your product is pending approval. Please contact support at support."
}
```

**Validation Errors (400 Bad Request):**

**Missing required fields:**
```json
{
  "name_ar": ["This field is required."],
  "category": ["This field is required."],
  "governorate": ["This field is required."],
  "wilayat": ["This field is required."],
  "price": ["This field is required."],
  "description": ["This field is required."],
  "contact_phone": ["This field is required."],
  "images": ["This field is required."]
}
```

**Invalid subcategory for category:**
```json
{
  "subcategory": ["This subcategory does not belong to the selected category."]
}
```

**Invalid wilayat for governorate:**
```json
{
  "wilayat": ["Wilayat 'Muttrah' is not valid for governorate 'Dhofar'."]
}
```

**No images provided:**
```json
{
  "images": ["At least one image is required."]
}
```

**Too many images:**
```json
{
  "images": ["At most 5 images allowed."]
}
```

**Price below minimum:**
```json
{
  "price": ["Price must be at least 10.00."]
}
```

**Invalid phone format:**
```json
{
  "contact_phone": ["Phone must follow Egyptian format (+20XXXXXXXXXX) or Omani format (+968XXXXXXXX)"]
}
```

**Invalid category ID:**
```json
{
  "category": ["Invalid pk \"999\" - object does not exist."]
}
```

**Invalid name characters:**
```json
{
  "name_en": ["Full name English must contain only English letters and spaces."],
  "name_ar": ["Full name Arabic must contain only Arabic letters and spaces."]
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

**Description:** Retrieve full product details. **Important:** Views count is automatically incremented with each request.

**Permissions:** Public (no authentication required)

**Request Headers:**
```
(No authentication required)
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_full_name_en": "Ahmed Al Balushi",
  "user_full_name_ar": "أحمد البلوشي",
  "category": 1,
  "category_name_en": "Electronics",
  "category_name_ar": "إلكترونيات",
  "subcategory": 10,
  "subcategory_name_en": "Phones",
  "subcategory_name_ar": "هواتف",
  "name_en": "iPhone 14",
  "name_ar": "آيفون 14",
  "governorate": "Muscat",
  "wilayat": "Muscat",
  "price": "350.00",
  "description": "Brand new iPhone 14 with warranty.",
  "contact_phone": "+96891234567",
  "whatsapp_url": "https://wa.me/96891234567",
  "image_urls": [
    { "url": "https://res.cloudinary.com/your-cloud/image/upload/v123/file.jpg" }
  ],
  "status": "active",
  "ad": false,
  "posted_at": "2025-10-09T12:34:56Z"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 4. Update Product
**Endpoint:** `PUT /api/products/{id}/` or `PATCH /api/products/{id}/`

**Description:** Update a product listing. Only the product owner can update their own products.

**Permissions:** Authenticated users only (must be the owner)

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data) - Full Update (PUT):**
```
category: 1 (required)
subcategory: 10 (optional)
name_en: "iPhone 14 Pro" (optional)
name_ar: "آيفون 14 برو" (required)
governorate: "Muscat" (required)
wilayat: "Muscat" (required)
price: 400.00 (required)
description: "Updated description" (required)
contact_phone: "+96891234567" (required)
images: [<file1>, <file2>] (required for PUT, 1-5 files)
```

**Request Body (Form Data) - Partial Update (PATCH):**
```
price: 400.00
description: "Updated description with new price"
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_full_name_en": "Ahmed Al Balushi",
  "user_full_name_ar": "أحمد البلوشي",
  "category": 1,
  "category_name_en": "Electronics",
  "category_name_ar": "إلكترونيات",
  "subcategory": 10,
  "subcategory_name_en": "Phones",
  "subcategory_name_ar": "هواتف",
  "name_en": "iPhone 14 Pro",
  "name_ar": "آيفون 14 برو",
  "governorate": "Muscat",
  "wilayat": "Muscat",
  "price": "400.00",
  "description": "Updated description",
  "contact_phone": "+96891234567",
  "whatsapp_url": "https://wa.me/96891234567",
  "image_urls": [
    { "url": "https://res.cloudinary.com/your-cloud/image/upload/v123/new_file.jpg" }
  ],
  "status": "active",
  "ad": false,
  "posted_at": "2025-10-09T12:34:56Z"
}
```

**Error Response (403 Forbidden) - Not the owner:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

### 5. Delete Product (Soft Delete)
**Endpoint:** `DELETE /api/products/{id}/`

**Description:** Delete a product listing. This is a **soft delete** - the product status is changed to "inactive" and it will no longer be visible in public listings. Only the product owner can delete their own products.

**Permissions:** Authenticated users only (must be the owner)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content):**
```
(Empty body)
```

**Error Response (403 Forbidden) - Not the owner:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Ad Request Endpoints

### 1. Create Ad Request
**Endpoint:** `POST /api/ads/request/`

**Description:** Submit a request to mark your product as a paid advertisement. Each user can request an ad for a product only once. After submission, the support team will contact you via phone or WhatsApp to arrange payment and ad scheduling.

**Permissions:** Authenticated users only

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{ "product": 123 }
```

**Field Requirements:**
- **product** (required): Product ID for which the ad request is being made (must be your own product)

**Response (201 Created):**
```json
{
  "id": 1,
  "product": 123,
  "is_approved": false,
  "ad_start": null,
  "ad_end": null,
  "created_at": "2025-10-09T12:34:56Z",
  "message": "Ad request successful. Our team will contact you soon via phone or WhatsApp."
}
```

**Error Response (400 Bad Request) - Not your product:**
```json
{ "non_field_errors": ["You can only request an ad for your own product."] }
```

**Error Response (400 Bad Request) - Duplicate request:**
```json
{ "non_field_errors": ["You already requested an ad for this product."] }
```

**Error Response (400 Bad Request) - Inactive product:**
```json
{ "non_field_errors": ["Cannot request ad for an inactive product."] }
```

**Error Response (400 Bad Request) - Invalid product:**
```json
{ "product": ["Invalid pk \"999\" - object does not exist."] }
```

**Error Response (401 Unauthorized):**
```json
{ "detail": "Authentication credentials were not provided." }
```

---

## Data Reference

### Governorate Options

All governorates must use the **English key** when submitting data. Filtering accepts both EN and AR.

| English Key | Arabic Name |
|-------------|-------------|
| `Muscat` | مسقط |
| `Dhofar` | ظفار |
| `Musandam` | مسندم |
| `Al Buraimi` | البريمي |
| `Ad Dakhiliyah` | الداخلية |
| `Al Batinah North` | شمال الباطنة |
| `Al Batinah South` | جنوب الباطنة |
| `Ash Sharqiyah North` | شمال الشرقية |
| `Ash Sharqiyah South` | جنوب الشرقية |
| `Ad Dhahirah` | الظاهرة |
| `Al Wusta` | الوسطى |

### Wilayat Options

All wilayats must use the **English key** when submitting data. Each wilayat belongs to a specific governorate. Filtering accepts both EN and AR.

**Muscat:**
- `Muscat` (مسقط), `Muttrah` (مطرح), `Al Amarat` (العامرات), `Bawshar` (بوشر), `Al Seeb` (السيب), `Qurayyat` (قريات)

**Dhofar:**
- `Salalah` (صلالة), `Taqah` (طاقة), `Mirbat` (مرباط), `Rakhyut` (رخيوت), `Thumrait` (ثمريت), `Dhalkut` (ضلكوت), `Al Mazyunah` (المزيونة), `Muqshin` (مقشن), `Shalim & Hallaniyat Islands` (شليم وجزر الحلانيات), `Sadah` (سدح)

**Musandam:**
- `Khasab` (خصب), `Dibba` (دبا), `Bukha` (بخا), `Madha` (مدحاء)

**Al Buraimi:**
- `Al Buraimi` (البريمي), `Mahdha` (ومضة), `Al Sunainah` (السنينة)

**Ad Dakhiliyah:**
- `Nizwa` (نزوى), `Samail` (سمائل), `Bahla` (بهلاء), `Adam` (أدم), `Al Hamra` (الحمراء), `Manah` (منح), `Izki` (إزكي), `Bidbid` (بدبد), `Jebel Akhdar` (الجبل الأخضر)

**Al Batinah North:**
- `Sohar` (صحار), `Shinas` (شناص), `Liwa` (لوى), `Saham` (صحم), `Al Khaburah` (الخابورة), `Al Suwaiq` (السويق)

**Al Batinah South:**
- `Rustaq` (الرستاق), `Al Awabi` (العوابي), `Nakhl` (نخل), `Wadi Al Maawil` (وادي المعاول), `Barka` (بركاء), `Al Musannah` (المصنعة)

**Ash Sharqiyah North:**
- `Ibra` (إبراء), `Mudhaibi` (المضيبي), `Bidiyah` (بدية), `Al Qabil` (القابل), `Wadi Bani Khalid` (وادي بني خالد), `Demaa Wa Al Tayin` (دماء والطائيين)

**Ash Sharqiyah South:**
- `Sur` (صور), `Al Kamil Wa Al Wafi` (الكامل والوافي), `Jaalan Bani Bu Hasan` (جعلان بني بو حسن), `Jaalan Bani Bu Ali` (جعلان بني بو علي), `Masirah` (مصيرة)

**Ad Dhahirah:**
- `Ibri` (عبري), `Yanqul` (ينقل), `Dank` (ضنك)

**Al Wusta:**
- `Haima` (هيماء), `Mahout` (محوت), `Duqm` (الدقم), `Al Jazer` (الجازر)

---

## Product Status Values

Products can have one of three status values:

| Status | Description |
|--------|-------------|
| `active` | Product is visible to all users and appears in listings |
| `pending` | Product is awaiting admin approval (quota exceeded) |
| `inactive` | Product has been soft-deleted by the owner (not visible) |

**Note:** Only `active` products are shown in public listings. Users only see products with `status: "active"`.

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
| 403 | Forbidden | Authenticated but lacking permissions (e.g., not the owner) |
| 404 | Not Found | Resource doesn't exist |

---

## Notes & Best Practices

### 1. Image Upload (Cloudinary)
- Each product can store up to **5 images maximum**
- If you upload more than 5 images, only the first 5 are saved
- Supported formats: JPG, PNG, GIF, WebP

### 2. Phone Number & WhatsApp
- Contact phone must be in Egyptian (+20XXXXXXXXXX) or Omani (+968XXXXXXXX) format
- Egyptian format: `+20` followed by exactly 10 digits
- Omani format: `+968` followed by exactly 8 digits
- The WhatsApp URL is automatically generated from this number
- Format examples: 
  - Egyptian: `https://wa.me/20XXXXXXXXXX`
  - Omani: `https://wa.me/968XXXXXXXX`

### 3. Governorate/Wilayat Validation
- The system validates that the wilayat belongs to the selected governorate
- Invalid combinations will be rejected with a 400 error
- When **submitting data**, use the **English keys** (e.g., "Muscat", not "مسقط")
- When **filtering**, you can use both Arabic and English (case-insensitive, partial match)

### 4. Subcategory Validation
- If a subcategory is provided, it must belong to the selected category
- Subcategory is optional - you can create a product with just a category
- When subcategory is null, the response will show `subcategory: null`, `subcategory_name_en: null`, `subcategory_name_ar: null`

### 5. Product Names
- `name_ar` is **required** for all products
- `name_en` is **optional** and can be null
- When `name_en` is not provided, it will be transakted from arabic name in responses
### 6. Search Functionality
- The `search` parameter searches across product names (Arabic and English), category names (Arabic and English), and subcategory names (Arabic and English)
- Search is case-insensitive and supports partial matches
- Works with both Arabic and English text

### 7. Bilingual Filtering
- Filters for `category`, `subcategory`, `governorate`, and `wilayat` accept both English and Arabic
- Filtering is case-insensitive and supports partial matches
- The system internally maps Arabic names to English keys

### 8. Multiple Filters
- You can combine multiple query parameters for complex filtering
- Example: `GET /api/products/?category=إلكترونيات&governorate=Muscat&min_price=100&max_price=500&ordering=-price`
- All filters work together (AND logic)

### 9. Default Ordering
- Products are sorted by newest first (`-posted_at`) by default
- You can override this with the `ordering` parameter

### 10. Multipart Form Data
- When creating a product, you must use `Content-Type: multipart/form-data`
- This is required because you're uploading image files
- All text fields should be sent as form fields, not JSON
- Images should be sent as file uploads

### 11. User Assignment
- The product owner (`user` field) is automatically set to the authenticated user
- You cannot manually specify the user when creating a product

### 12. Product Ownership & Permissions
- Only the product **owner** can update or delete their own products
- Attempting to update/delete someone else's product will return a 403 Forbidden error
- Authentication is required for creating, updating, and deleting products

### 13. Soft Delete
- When a user deletes a product, it's a **soft delete**
- The product's status is changed to `inactive` and it's no longer visible in public listings

### 14. Monthly Quota
- Users have a monthly quota for free product postings (default: 4 products per month)
- The quota resets at the beginning of each month
- If you exceed your quota, new products will have `status: "pending"` and require admin approval
- You'll receive a message in the response explaining the situation
- Only active and pending products count toward your monthly quota (inactive/deleted products don't count)

### 15. Ad Products
- Products with `ad: true` are paid advertisements
- These products appear prominently in listings
- To request an ad for your product, use the `/api/ads/request/` endpoint
- The support team will contact you to arrange payment and scheduling

### 16. Product Status Lifecycle
- **Active**: Normal visible product
- **Pending**: Awaiting admin approval (quota exceeded)
- **Inactive**: Soft-deleted by owner (not visible to public)

---

## Endpoints Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/categories/` | No | List all categories (paginated, 20 per page) |
| GET | `/api/categories/{id}/` | No | Get category with subcategories |
| GET | `/api/subcategories/` | No | List all subcategories (paginated, 20 per page) |
| GET | `/api/products/` | No | List all active products (paginated, filters) |
| POST | `/api/products/` | Yes | Create a new product |
| GET | `/api/products/{id}/` | No | Get product details (increments views) |
| PUT/PATCH | `/api/products/{id}/` | Yes (owner) | Update product |
| DELETE | `/api/products/{id}/` | Yes (owner) | Soft delete product |
| POST | `/api/ads/request/` | Yes | Request ad for your product |

---
