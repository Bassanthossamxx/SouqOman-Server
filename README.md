# SouqOman-Server

A modular Django + Django REST Framework backend for an OLX‑style classifieds / e‑commerce platform (SouqOman). It includes a clean structure ready for implementing listings, users, carts and orders.

---
## 1. Key Features

Current:
- Modular apps: `users`, `products`, `orders`, `cart`
- PostgreSQL via `DATABASE_URL` (works great with Neon: https://neon.tech)
- Environment variables through `python-decouple` / `.env`
- Django Admin enabled
- DRF ready (no endpoints added yet)

---
## 2. Tech Stack
- Python 3.12+
- Django 5.2
- Django REST Framework
- PostgreSQL (Neon serverless or local)
- `python-decouple`, `python-dotenv`

---
## 3. Project Structure
```
manage.py
core/
  settings.py
  urls.py
  asgi.py / wsgi.py
apps/
  users/
  products/
  orders/
  cart/
requirements.txt
```
Each app has:
```
models.py | views.py | admin.py | tests.py | apps.py | migrations/ | serializers.py (empty) | urls.py (empty)
```
---
## 4. Quick Start (Local)

1. Clone
```bash
git clone <repo-url> SouqOman-Server
cd SouqOman-Server
```
2. Virtual env (Windows CMD)
```bash
python -m venv .venv
.venv\Scripts\activate
```
3. Install deps
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
4. Create `.env`
```bash
SECRET_KEY=change_me
DEBUG=True
DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DB_NAME
```
(For Neon: copy the connection string from the Neon dashboard: https://neon.tech)

5. (Optional) Generate a secure key
```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```
6. Migrate
```bash
python manage.py migrate
```
7. Admin user
```bash
python manage.py createsuperuser
```
8. Run server
```bash
python manage.py runserver
```
Visit: http://127.0.0.1:8000/admin/

---
## 5. Environment Variables
| Name         | Required | Purpose                      | Example |
|--------------|----------|------------------------------|---------|
| SECRET_KEY   | Yes      | Django security key          | (random) |
| DEBUG        | Yes      | Dev = True / Prod = False    | True |
| DATABASE_URL | Yes      | PostgreSQL connection string | postgres://user:pw@host:5432/db |

---
## 6. Database Notes
The project parses `DATABASE_URL` into Django's DB settings. Make sure the database exists first.
---
### Summary
This README only provides the setup and structure details for the project. It does NOT mean the business logic, models, or API features are already implemented. Use it as a guide to configure the environment.
@bassanthossamxx