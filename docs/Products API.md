# Products API Documentation

**Base URL:** `/api/`

**Authentication:** JWT (Authorization: `Bearer <token>`)

---

## Table of Contents
1. [Authentication & Permissions](#authentication--permissions)
2. [Category Endpoints](#category-endpoints)
3. [SubCategory Endpoints](#subcategory-endpoints)
4. [Product Endpoints](#product-endpoints)

---

## Authentication & Permissions

- **Authentication Method:** JWT tokens via Authorization header
- **Header Format:** `Authorization: Bearer <access_token>`
- **Permissions:**
  - **Categories & Subcategories:** 
    - Read (GET): Public access
    - Write (POST/DELETE): Superuser only
  - **Products:**
    - List (GET /products/): Public access (no authentication required)
    - Create (POST /products/): Authenticated users only
    - Retrieve (GET /products/{id}/): Public access (no authentication required)

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

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "name_en": "Electronics",
    "name_ar": "إلكترونيات"
  },
  {
    "id": 2,
    "name_en": "Fashion",
    "name_ar": "أزياء"
  }
]
```

**Response for Empty Database (200 OK):**
```json
[]
```

---

### 2. Create Category
**Endpoint:** `POST /api/categories/`

**Description:** Create a new category.

**Permissions:** Superuser only

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name_en": "Electronics",
  "name_ar": "إلكترونيات"
}
```

**Field Requirements:**
- **name_en** (required): English name, must contain only English letters and spaces, must be unique
- **name_ar** (required): Arabic name, must contain only Arabic letters and spaces, must be unique

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
- `name_en` must contain only English letters and spaces
- `name_ar` must contain only Arabic letters and spaces

**Error Response (400 Bad Request) - Duplicate name:**
```json
{
  "name_ar": ["category with this name ar already exists."],
  "name_en": ["category with this name en already exists."]
}
```

**Error Response (400 Bad Request) - Invalid characters:**
```json
{
  "name_en": ["Full name English must contain only English letters and spaces."],
  "name_ar": ["Full name Arabic must contain only Arabic letters and spaces."]
}
```

**Error Response (400 Bad Request) - Missing fields:**
```json
{
  "name_en": ["This field is required."],
  "name_ar": ["This field is required."]
}
```

**Error Response (401 Unauthorized) - Not authenticated:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Error Response (403 Forbidden) - Not superuser:**
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

**Response (200 OK) - Category with no subcategories:**
```json
{
  "id": 2,
  "name_en": "Fashion",
  "name_ar": "أزياء",
  "subcategories": []
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

**Description:** Delete a category. **Warning:** This will cascade delete all associated subcategories and products.

**Permissions:** Superuser only

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content):** 
```
(Empty body)
```

**Error Responses:**

**404 Not Found:** 
```json
{
  "detail": "Not found."
}
```

**401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
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

**Response (200 OK):**
```json
[
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
  },
  {
    "id": 12,
    "name_en": "Dresses",
    "name_ar": "فساتين",
    "category": 2
  }
]
```

**Response for Empty Database (200 OK):**
```json
[]
```

---

### 2. Create SubCategory
**Endpoint:** `POST /api/subcategories/`

**Description:** Create a new subcategory under a category.

**Permissions:** Superuser only

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "name_en": "Tablets",
  "name_ar": "أجهزة لوحية",
  "category": 1
}
```

**Field Requirements:**
- **name_en** (required): English name, must contain only English letters and spaces
- **name_ar** (required): Arabic name, must contain only Arabic letters and spaces
- **category** (required): Category ID (must exist)
- **Unique together:** (`category`, `name_en`) and (`category`, `name_ar`)

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
- Same subcategory name can exist in different categories
- `name_en` must contain only English letters and spaces
- `name_ar` must contain only Arabic letters and spaces

**Error Response (400 Bad Request) - Duplicate within category:**
```json
{
  "non_field_errors": ["The fields category, name_en must make a unique set."]
}
```

**Error Response (400 Bad Request) - Invalid category ID:**
```json
{
  "category": ["Invalid pk \"999\" - object does not exist."]
}
```

**Error Response (400 Bad Request) - Missing fields:**
```json
{
  "name_en": ["This field is required."],
  "name_ar": ["This field is required."],
  "category": ["This field is required."]
}
```

**Error Response (400 Bad Request) - Invalid characters:**
```json
{
  "name_en": ["Full name English must contain only English letters and spaces."],
  "name_ar": ["Full name Arabic must contain only Arabic letters and spaces."]
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Error Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Product Endpoints

### 1. List All Products (with Filtering, Searching, Sorting)
**Endpoint:** `GET /api/products/`

**Description:** Retrieve all products with support for bilingual filtering (EN/AR), searching, and sorting.

**Permissions:** Public (no authentication required)

**Request Headers:**
```
(No authentication required)
```

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `search` | string | Free-text search across product names and category/subcategory names (AR/EN) | `?search=هاتف` |
| `name` | string | Filter by product name (AR or EN, partial, case-insensitive) | `?name=iphone` |
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
- `GET /api/products/?name=iphone` - Products with "iphone" in name
- `GET /api/products/?category=إلكترونيات&ordering=-price` - Electronics sorted by price (high to low)
- `GET /api/products/?subcategory=هواتف&min_price=50&max_price=500` - Phones between 50-500
- `GET /api/products/?governorate=مسقط` - Products in Muscat governorate
- `GET /api/products/?wilayat=مطرح` - Products in Muttrah wilayat
- `GET /api/products/?governorate=Muscat&wilayat=Muttrah&ordering=-views_count` - Most viewed in Muscat/Muttrah
- `GET /api/products/?min_price=100&max_price=1000&ordering=price` - Products 100-1000, cheapest first

**Response (200 OK):**
```json
[
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
      { "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file.jpg" }
    ]
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
      { "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file1.jpg" },
      { "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file2.jpg" }
    ]
  }
]
```

**Response for Empty Results (200 OK):**
```json
[]
```

**Response for No Matches (200 OK):**
```json
[]
```

---

### 2. Create Product
**Endpoint:** `POST /api/products/`

**Description:** Create a new product listing. The authenticated user will be automatically set as the product owner.

**Permissions:** Authenticated users only

**Request Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Content-Type:** `multipart/form-data`

**Request Body (Form Data):**
```
category: 1 (required)
subcategory: 10 (optional, can be null/omitted)
name_en: "iPhone 14" (optional, can be null/omitted)
name_ar: "آيفون 14" (required)
governorate: "Muscat" (required)
wilayat: "Muscat" (required)
price: 350.00 (required)
description: "Brand new iPhone 14." (required)
contact_phone: "+96891234567" (required)
images: [<file1>, <file2>, ...] (required, 1-5 files)
```

**Field Requirements:**

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `category` | integer | Yes | Must be valid category ID | - |
| `subcategory` | integer | No | Must belong to selected category | Can be null/omitted |
| `name_en` | string | No | Only English letters and spaces | Can be null/omitted |
| `name_ar` | string | Yes | Only Arabic letters and spaces | - |
| `governorate` | string | Yes | Must be valid governorate key (EN) | See [Governorate Options](#governorate-options) |
| `wilayat` | string | Yes | Must be valid wilayat for selected governorate | See [Wilayat Options](#wilayat-options) |
| `price` | decimal | Yes | Minimum 10.00 | Max 10 digits, 2 decimal places |
| `description` | text | Yes | - | No length limit |
| `contact_phone` | string | Yes | Must be +968XXXXXXXX format | 8 digits after +968 |
| `images` | files | Yes | 1-5 image files | If >5 uploaded, only first 5 saved |

**Response (201 Created):**
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
    { "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file.jpg" }
  ]
}
```

**Response Example - Product without subcategory:**
```json
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
    { "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file1.jpg" },
    { "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file2.jpg" }
  ]
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

**Price below minimum:**
```json
{
  "price": ["Price must be at least 10.00."]
}
```

**Invalid phone format:**
```json
{
  "contact_phone": ["Phone must follow Omani format: +968XXXXXXXX"]
}
```

**Invalid category ID:**
```json
{
  "category": ["Invalid pk \"999\" - object does not exist."]
}
```

**Invalid subcategory ID:**
```json
{
  "subcategory": ["Invalid pk \"999\" - object does not exist."]
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

**Description:** Retrieve full product details. **Important:** Views count is automatically incremented with each request (including this one).

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
    { "url": "https://res.cloudinary.com/<cloud_name>/image/upload/v.../file.jpg" }
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
| `Al Batinah North` | الباطنة شمال |
| `Al Batinah South` | الباطنة جنوب |
| `Ash Sharqiyah North` | الشرقية شمال |
| `Ash Sharqiyah South` | الشرقية جنوب |
| `Ad Dhahirah` | الظاهرة |
| `Al Wusta` | الوسطى |

### Wilayat Options

All wilayats must use the **English key** when submitting data. Each wilayat belongs to a specific governorate. Filtering accepts both EN and AR.

**Muscat:**
- `Muscat` (مسقط), `Muttrah` (مطرح), `Al Amarat` (العامرات), `Bawshar` (بوشر), `Al Seeb` (السيب), `Qurayyat` (قريات)

**Dhofar:**
- `Salalah` (صلالة), `Taqah` (طاقة), `Mirbat` (مرباط), `Rakhyut` (رخيوت), `Thumrait` (ثمريت), `Dhalkut` (ضلكوت), `Al Mazyunah` (المزيونة), `Muqshin` (مقشن), `Shalim & Hallaniyat Islands` (شليم و جزر الحلانيات), `Sadah` (سدح)

**Musandam:**
- `Khasab` (خصب), `Dibba` (دبا), `Bukha` (بخا), `Madha` (مدحا)

**Al Buraimi:**
- `Al Buraimi` (البريمي), `Mahdha` (محضة), `Al Sunainah` (السنينة)

**Ad Dakhiliyah:**
- `Nizwa` (نزوى), `Samail` (سمائل), `Bahla` (بهلا), `Adam` (آدم), `Al Hamra` (الحمراء), `Manah` (منح), `Izki` (إزكي), `Bidbid` (بدبد), `Jebel Akhdar` (الجبل الأخضر)

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
| 403 | Forbidden | Authenticated but lacking permissions (e.g., not superuser) |
| 404 | Not Found | Resource doesn't exist |

---

## Notes & Best Practices

1. **Views Count:** The `views_count` field is automatically incremented each time a product detail is accessed via `GET /api/products/{id}/`. You don't need to manually update it. This happens on every request, including from the same user.

2. **Image Upload (Cloudinary):** 
   - Images are uploaded to Cloudinary automatically upon product creation
   - Each product can store up to 5 images
   - If you upload more than 5 images, only the first 5 are saved
   - Images are returned as an array of objects with `url` field (secure HTTPS URL)
   - Supported formats: JPG, PNG, GIF, WebP
   - The local file is automatically deleted after upload to Cloudinary

3. **Phone Number & WhatsApp:** 
   - Contact phone must be in Omani format (`+968XXXXXXXX`)
   - Must start with `+968` followed by exactly 8 digits
   - The WhatsApp URL is automatically generated from this number
   - Format: `https://wa.me/968XXXXXXXX` (the + is removed in the URL)

4. **Governorate/Wilayat Validation:** 
   - The system validates that the wilayat belongs to the selected governorate
   - Invalid combinations will be rejected with a 400 error
   - When submitting data, use the **English keys** (e.g., "Muscat", not "مسقط")
   - Filtering supports both EN and AR (case-insensitive, partial match)

5. **Subcategory Validation:** 
   - If a subcategory is provided, it must belong to the selected category
   - Subcategory is optional - you can create a product with just a category
   - When subcategory is null, the response will show `subcategory: null`, `subcategory_name_en: null`, `subcategory_name_ar: null`

6. **Product Names:**
   - `name_ar` is required for all products
   - `name_en` is optional and can be null
   - When `name_en` is not provided, it will be `null` in responses

7. **Search Functionality:** 
   - The `search` parameter searches across product names (Arabic and English), category names (Arabic and English), and subcategory names (Arabic and English)
   - Search is case-insensitive and supports partial matches
   - Works with both Arabic and English text

8. **Bilingual Filtering:**
   - Filters for `category`, `subcategory`, `governorate`, and `wilayat` accept both English and Arabic
   - Filtering is case-insensitive and supports partial matches
   - The system internally maps Arabic names to English keys

9. **Multiple Filters:** 
   - You can combine multiple query parameters for complex filtering
   - Example: `GET /api/products/?category=إلكترونيات&governorate=Muscat&min_price=100&max_price=500&ordering=-price`
   - All filters work together (AND logic)

10. **Default Ordering:**
    - Products are sorted by newest first (`-posted_at`) by default
    - You can override this with the `ordering` parameter

11. **Multipart Form Data:**
    - When creating a product, you must use `Content-Type: multipart/form-data`
    - This is required because you're uploading image files
    - All text fields should be sent as form fields, not JSON
    - Images should be sent as file uploads

12. **User Assignment:**
    - The product owner (`user` field) is automatically set to the authenticated user
    - You cannot manually specify the user when creating a product
    - User's full name (EN and AR) is included in product responses

13. **Authentication vs. Public Access:**
    - **No auth needed:** List products, view product details, list categories/subcategories, view category details
    - **Auth required:** Create products
    - **Superuser required:** Create/delete categories and subcategories

---
