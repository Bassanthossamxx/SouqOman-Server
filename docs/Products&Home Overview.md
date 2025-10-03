
# Products & Categories Overview

Entities: **PRODUCT, CATEGORY, SUBCATEGORY, AD**

---

## CATEGORY

| Field            | Type   | Notes            |
| ---------------- | ------ | ---------------- |
| category_id (PK) | int    | Primary key      |
| name_en          | string | Required, unique |
| name_ar          | string | Required, unique |

---

## SUBCATEGORY

| Field               | Type   | Notes               |
| ------------------- | ------ | ------------------- |
| subcategory_id (PK) | int    | Primary key         |
| category_id (FK)    | int    | References CATEGORY |
| name_en             | string | Required            |
| name_ar             | string | Required            |

---

## PRODUCT

| Field               | Type     | Notes                                 |
| ------------------- | -------- |---------------------------------------|
| product_id (PK)     | int      | Primary key                           |
| name_en             | string   | Optional                              |
| name_ar             | string   | **Required**                          |
| governorate         | string   | Required                              |
| wilayat             | string   | Required                              |
| images        | list     | 0–7 additional images                 |
| price               | decimal  | ≥ 0                                   |
| description         | string   | Required                              |
| posted_at           | datetime | Auto                                  |
| views_count         | int      | Auto-increment                        |
| contact_phone       | string   | **Required, must support WhatsApp**   |
| category_id (FK)    | int      | Required                              |
| subcategory_id (FK) | int      | Optional                              |

---

## AD

| Field           | Type     | Notes                            |
| --------------- | -------- | -------------------------------- |
| ad_id (PK)      | int      | Primary key                      |
| product_id (FK) | int      | One-to-one with PRODUCT          |
| is_active       | boolean  | If true, product is marked as Ad |
| start_date      | datetime | Required if active               |
| duration_days   | int      | Expiry logic                     |

---

## Rules

* `name_ar` required (name_en optional).
* `subcategory_id` must belong to same `category_id`.
* Governorate & wilayat must be valid.
* Price ≥ 0.
* Phone required, must be WhatsApp-valid (`+968XXXXXXXX`).
* Every product has one cover image, optional extra images.

---

## Filtering & Search

* **Search** → `?search=` (across `name_ar`, `name_en`).
* **Filter** → `category_id`, `subcategory_id`, `price_min`, `price_max`, `governorate`, `wilayat`.
* **Sort** → `-posted_at` (newest, default), `posted_at` (oldest), `price`, `-price`.

---

## Response Rules

* Each product response includes:

    * `is_ad` → true/false (from AD table).
    * `whatsapp_link` → `https://wa.me/{contact_phone}`.
    * Cover + other images separated.

---

## Example Response (List)

```json
{
  "count": 1,
  "results": [
    {
      "product_id": 51,
      "name_ar": "ايفون 15 برو",
      "name_en": "iPhone 15 Pro",
      "price": 450.0,
      "cover_image": "https://cdn.ex.com/51/cover.jpg",
      "other_images": [
        "https://cdn.ex.com/51/1.jpg",
        "https://cdn.ex.com/51/2.jpg"
      ],
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
  ]
}
```
