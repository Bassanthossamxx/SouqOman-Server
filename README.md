# SouqOman-Server

A modular Django + Django REST Framework backend for an OLX‑style classifieds / e‑commerce platform (SouqOman). It includes a complete authentication system, products management with categories, image uploads to Cloudinary, and comprehensive filtering/search capabilities.

---
## 1. Key Features

### Implemented Features:
- **Authentication System**: JWT-based authentication with access/refresh tokens
  - User registration with OTP verification
  - Login/logout with token blacklisting
  - Profile management (update, change password)
  - Custom User model with Arabic/English names
  
- **Products Management**:
  - Categories and subcategories with Arabic/English names
  - Product listings with image uploads (up to 5 images per product)
  - Advanced filtering by category, subcategory, price, location (governorate/wilayat)
  - Search functionality across product/category names (Arabic & English)
  - Sorting by price, date, and view count
  - Auto-incrementing view counter for product details
  - WhatsApp integration for contact
  
- **Image Storage**: Cloudinary integration for cloud-based image management
- **Location System**: Governorate and Wilayat validation for Oman
- **Database**: PostgreSQL via `DATABASE_URL` (works great with Neon: https://neon.tech)
- **Environment Variables**: Managed through `python-decouple` / `.env`
- **Django Admin**: Fully enabled with custom user management

### Planned Features:
- Shopping cart functionality
- Order management system
- Featured ads/promotions
- User favorites/bookmarks
- Advanced analytics

---
## 2. Tech Stack
- **Python** 3.12+
- **Django** 5.2.6
- **Django REST Framework** 3.16.1
- **PostgreSQL** (Neon serverless or local)
- **Cloudinary** 1.44.1 (Cloud image storage)
- **Django Filter** 25.2 (Advanced filtering)
- **JWT Authentication** (djangorestframework-simplejwt)
- **Environment Management**: python-decouple, python-dotenv

---
## 3. Project Structure
```
SouqOman-Server/
├── manage.py
├── requirements.txt
├── .env (create this)
├── core/
│   ├── settings.py          # Main settings with Cloudinary config (via CLOUDINARY_URL)
│   ├── urls.py              # Root URL configuration
│   ├── choices.py           # Governorate/Wilayat mappings
│   ├── validators.py        # Custom validators (phone, names)
│   ├── permissions.py       # Custom DRF permissions
│   ├── utils.py             # Utilities (helpers)
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── users/
│   │   ├── models.py        # Custom User model
│   │   ├── serializers.py   # Auth serializers
│   │   ├── views.py         # Auth endpoints
│   │   ├── urls.py          # Auth routes
│   │   ├── admin.py
│   │   └── migrations/
│   ├── products/
│   │   ├── models.py        # Category, SubCategory, Product, ProductImage (Cloudinary-backed)
│   │   ├── serializers.py   # Product serializers
│   │   ├── views.py         # Product CRUD & filtering
│   │   ├── urls.py          # Product routes
│   │   ├── admin.py
│   │   └── migrations/
│   ├── orders/              # (Planned)
│   │   └── ...
│   └── cart/                # (Planned)
│       └── ...
└── docs/
    ├── authentication api doc.md
    ├── Authentication System Overview.md
    ├── Products API.md
    ├── Products&Home Overview.md
    └── SouqOman ERD.png
```

---
## 4. Quick Start (Local)

### 1. Clone the Repository
```bash
git clone <repo-url> SouqOman-Server
cd SouqOman-Server
```

### 2. Create Virtual Environment (Windows CMD)
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create `.env` File
Create a `.env` file in the root directory with the following variables:
```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (Neon PostgreSQL)
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DB_NAME

# Cloudinary Configuration
# Format: cloudinary://<api_key>:<api_secret>@<cloud_name>
CLOUDINARY_URL=cloudinary://your_api_key:your_api_secret@your_cloud_name
```

**To get Cloudinary credentials:**
1. Sign up at https://cloudinary.com
2. Go to your Dashboard
3. Copy your Cloud name, API Key, and API Secret and form the `CLOUDINARY_URL`

### 5. (Optional) Generate a Secure Secret Key
```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

### 6. Run Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Visit:
- Admin Panel: http://127.0.0.1:8000/admin/
- API Documentation: See `docs/` folder

---
## 5. Environment Variables

| Name            | Required | Purpose                          | Example                                              |
|-----------------|----------|----------------------------------|------------------------------------------------------|
| SECRET_KEY      | Yes      | Django security key              | (random string from generator)                       |
| DEBUG           | Yes      | Dev = True / Prod = False        | True                                                 |
| DATABASE_URL    | Yes      | PostgreSQL connection string     | postgres://user:pw@host:5432/db                      |
| CLOUDINARY_URL  | Yes      | Cloudinary connection string     | cloudinary://api_key:api_secret@cloud_name           |

---
## 6. API Endpoints

### Authentication (`/api/auth/`)
- `POST /api/auth/register/` - User registration with OTP
- `POST /api/auth/verify-otp/` - Verify OTP code
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/logout/` - Logout and blacklist token
- `POST /api/auth/token/refresh/` - Refresh access token
- `GET /api/auth/profile/` - Get user profile
- `PATCH /api/auth/profile/update/` - Update profile
- `POST /api/auth/change-password/` - Change password

### Products (`/api/`)
- `GET/POST /api/categories/` - List/create categories
- `GET/DELETE /api/categories/{id}/` - Category details/delete
- `GET/POST /api/subcategories/` - List/create subcategories
- `GET /api/products/` - List products (with filtering/search/sort)
- `POST /api/products/` - Create product (authenticated)
- `GET /api/products/{id}/` - Product details (auto-increments views)

**For detailed API documentation, see:**
- `docs/authentication api doc.md`
- `docs/Products API.md`

---
## 7. Features in Detail

### Product Filtering & Search
Products can be filtered by:
- Category name (Arabic/English)
- Subcategory name (Arabic/English)
- Price (exact match)
- Governorate and Wilayat
- Search across product/category/subcategory names

### Sorting Options
- Price: low to high, high to low
- Date: newest first, oldest first
- Views: most viewed, least viewed

### Image Upload
- Up to 5 images per product
- Uploaded to Cloudinary cloud storage
- Automatic secure URL generation
- Supports multiple image formats

### Location System
- Governorate/Wilayat validation for Oman
- Ensures wilayat belongs to selected governorate
- Predefined choices in `core/choices.py`

### WhatsApp Integration
- Auto-generates WhatsApp contact links
- Based on Omani phone number format (+968XXXXXXXX)
- Phone number validation included

---
## 8. Database Notes

The project parses `DATABASE_URL` into Django's database settings. 

**For Neon (Recommended):**
1. Create account at https://neon.tech
2. Create a new project
3. Copy the connection string
4. Add to `.env` as `DATABASE_URL`

**For Local PostgreSQL:**
```
DATABASE_URL=postgres://postgres:password@localhost:5432/souqoman_db
```

Make sure the database exists before running migrations.

---
## 9. Development Workflow

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Checking System
```bash
python manage.py check
```

### Collecting Static Files (Production)
```bash
python manage.py collectstatic
```

---
## 10. Documentation

The `docs/` directory contains detailed documentation:

- **Authentication System Overview.md** - Authentication flow and architecture
- **authentication api doc.md** - Complete auth API reference
- **Products API.md** - Complete products API reference with examples
- **Products&Home Overview.md** - Product feature specifications
- **SouqOman ERD.png** - Database entity relationship diagram

---
## 11. Security Notes

- JWT tokens with 6-hour access and 60-day refresh lifetime
- Token rotation and blacklisting enabled
- Custom validators for phone numbers and names (Arabic/English)
- Governorate/Wilayat validation to prevent invalid location data
- Subcategory-to-category validation
- Superuser-only access for category/subcategory management
---
## 12. License & Credits

All rights reserved to **@bassanthossamxx**

---
