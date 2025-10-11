# Authentication API Documentation

This document provides detailed information about the authentication endpoints for SouqOman platform. It covers user registration, login, logout, user details, token management processes, including request parameters, validation rules, error scenarios, and response formats.

## Authentication Endpoints
base url for all endpoints: `/api/auth/`

## Rate Limiting
To protect the platform from abuse, authentication endpoints are rate limited. If a client exceeds the limits below, the API responds with `429 Too Many Requests`.

Current limits:
- `POST /api/auth/login/`: 10 requests per minute
- `POST /api/auth/register/`: 5 requests per hour
- `POST /api/auth/logout/`: 30 requests per minute
- `POST /api/auth/token/`: 10 requests per minute
- `POST /api/auth/token/refresh/`: 30 requests per minute

Example 429 response:
```json
{
  "detail": "Request was throttled. Expected available in 30 seconds."
}
```

Notes:
- Limits are applied per client (e.g., per IP or authenticated user, depending on deployment).
- Windows for the above limits are fixed per the unit (per minute/per hour).

---

### 1. User Registration

Registers a new user in the system and automatically authenticates them (issues JWT access & refresh tokens). There is no need to call the login endpoint after a successful registration.

**Endpoint:** register/`

**Method:** `POST`

**Content-Type:** `application/json`

#### Request Body

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|-----------------|
| phone | string | Yes | User's phone number | Must follow Omani format: +968XXXXXXXX (8 digits after +968) |
| email | string | Yes | User's email address | Must be a valid email format and unique in the system |
| password | string | Yes | User's password | Must pass Django password validation (minimum 8 characters, not entirely numeric, not too common) |
| password2 | string | Yes | Password confirmation | Must match the password field exactly |
| full_name_ar | string | Yes | Full name in Arabic | Must contain only Arabic characters and spaces |
| full_name_en | string | Yes | Full name in English | Must contain only English letters and spaces |
| governorate | string | Yes | User's governorate | Must be one of the predefined governorates in Oman |
| wilayat | string | Yes | User's wilayat | Must be a valid wilayat within the selected governorate |

#### Example Request

```json
{
  "phone": "+96812345678",
  "email": "user@example.com",
  "password": "SecurePassword123",
  "password2": "SecurePassword123",
  "full_name_ar": "محمد أحمد",
  "full_name_en": "Mohammed Ahmed",
  "governorate": "Muscat",
  "wilayat": "Al Seeb"
}
```

#### Success Response (201 Created)

```json
{
  "message": "User registered successfully.",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Notes:
- The user is fully authenticated immediately.
- Store the tokens securely (prefer HTTP-only cookies or secure storage).

#### Error Responses

**400 Bad Request**

Various validation errors can occur. Here are the common ones:

* **Phone number validation:**
```json
{
  "phone": ["Phone must follow Omani format: +968XXXXXXXX"]
}
```

* **Email validation:**
```json
{
  "email": ["Enter a valid email address."]
}
```
or
```json
{
  "email": ["User with this email already exists."]
}
```

* **Password validation:**
```json
{
  "password": [
    "This password is too short. It must contain at least 8 characters.",
    "This password is too common.",
    "This password is entirely numeric."
  ]
}
```

* **Password mismatch:**
```json
{
  "passwords": ["Passwords must match."]
}
```

* **Name validation:**
```json
{
  "full_name_ar": ["Full name Arabic must contain only Arabic letters and spaces."]
}
```
or
```json
{
  "full_name_en": ["Full name English must contain only English letters and spaces."]
}
```

* **Governorate/Wilayat validation:**
```json
{
  "governorate": ["\"Invalid Governorate\" is not a valid choice."]
}
```
or
```json
{
  "wilayat": ["wilayat_name is not valid for governorate_name"]
}
```

* **429 Too Many Requests (rate limit exceeded):**
```json
{
  "detail": "Request was throttled. Expected available in 59 minutes."
}
```

### 2. User Login

Authenticates a user and provides access tokens.

**Endpoint:** `login/`

**Method:** `POST`

**Content-Type:** `application/json`

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone | string | Yes | User's phone number in format +968XXXXXXXX |
| password | string | Yes | User's password |

#### Example Request

```json
{
  "phone": "+96812345678",
  "password": "SecurePassword123"
}
```

#### Success Response (200 OK)

```json
{
  "message": "User logged in successfully.",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", 
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." 
}
```

#### Error Response (400 Bad Request)

```json
{
  "non_field_errors": ["Invalid phone or password."]
}
```

#### Error Response (429 Too Many Requests)
```json
{
  "detail": "Request was throttled. Expected available in 30 seconds."
}
```

### 3. User Logout

Logs out a user by blacklisting their refresh token.

**Endpoint:** `logout/`

**Method:** `POST`

**Content-Type:** `application/json`

**Authentication:** Requires a valid access token in the Authorization header.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refresh | string | Yes | The refresh token received during login or registration |

#### Example Request

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Success Response (205 Reset Content)

```json
{
  "detail": "Successfully logged out."
}
```

Additional Success (200 OK - idempotent):

```json
{
  "detail": "Already logged out."
}
```

Notes:
- Logout is idempotent. If the same refresh token is sent again after being blacklisted, the endpoint returns 200 OK with `"detail": "Already logged out."`.

#### Error Responses

**400 Bad Request**

```json
{
  "error": "Refresh token is required."
}
```

or

```json
{
  "error": "Invalid or expired refresh token."
}
```

**401 Unauthorized**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**429 Too Many Requests**
```json
{
  "detail": "Request was throttled. Expected available in 30 seconds."
}
```

### 4. User Details

Retrieves the authenticated user's profile details.

**Endpoint:** `me/`

**Method:** `GET`

**Authentication:** Requires a valid access token in the Authorization header.

#### Success Response (200 OK)

```json
{
  "id": 1,
  "phone": "+96812345678",
  "email": "user@example.com",
  "full_name_ar": "محمد أحمد",
  "full_name_en": "Mohammed Ahmed",
  "governorate": "Muscat",
  "wilayat": "Al Seeb"
}
```

#### Error Response (401 Unauthorized)

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 5. JWT Token Obtain

Alternative endpoint to obtain JWT tokens using standard JWT authentication.

**Endpoint:** `token/`

**Method:** `POST`

**Content-Type:** `application/json`

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | User's phone number (used as username) |
| password | string | Yes | User's password |

#### Example Request

```json
{
  "username": "+96812345678",
  "password": "SecurePassword123"
}
```

#### Success Response (200 OK)

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Error Response (401 Unauthorized)

```json
{
  "detail": "No active account found with the given credentials"
}
```

#### Error Response (429 Too Many Requests)
```json
{
  "detail": "Request was throttled. Expected available in 30 seconds."
}
```

### 6. JWT Token Refresh

Obtain a new access token using a valid refresh token.

**Endpoint:** `token/refresh/`

**Method:** `POST`

**Content-Type:** `application/json`

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refresh | string | Yes | The refresh token received during login or registration |

#### Example Request

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Success Response (200 OK)

```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." 
}
```

#### Error Response (401 Unauthorized)

```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

#### Error Response (429 Too Many Requests)
```json
{
  "detail": "Request was throttled. Expected available in 30 seconds."
}
```

## Authentication Flow (Updated)

1. Registration: Client sends user data to `register/`. On success, the backend returns both `access` and `refresh` tokens (auto-login). Store them securely immediately.
2. Authenticated Requests: Use the `access` token in `Authorization: Bearer <access>` for protected endpoints (e.g., `me/`).
3. Token Refresh: When the access token expires, send the `refresh` token to `token/refresh/` to receive a new access token.
4. Optional Manual Login: If a user registered earlier and logs out or their tokens are cleared, they can re-authenticate via `login/` or `/users/token/`.
5. Logout: Invalidate the session by POSTing the `refresh` token to `logout/`.

## Governorate and Wilayat Reference Data

### Available Governorates

- Muscat (مسقط)
- Dhofar (ظفار)
- Musandam (مسندم)
- Al Buraimi (البريمي)
- Ad Dakhiliyah (الداخلية)
- Al Batinah North (شمال الباطنة)
- Al Batinah South (جنوب الباطنة)
- Ash Sharqiyah North (شمال الشرقية)
- Ash Sharqiyah South (جنوب الشرقية)
- Ad Dhahirah (الظاهرة)
- Al Wusta (الوسطى)

### Wilayat by Governorate

**Muscat Governorate:**
- Muscat (مسقط)
- Muttrah (مطرح)
- Al Amarat (العامرات)
- Bawshar (بوشر)
- Al Seeb (السيب)
- Qurayyat (قريات)

**Dhofar Governorate:**
- Salalah (صلالة)
- Taqah (طاقة)
- Mirbat (مرباط)
- Rakhyut (رخيوت)
- Thumrait (ثمريت)
- Dhalkut (ضلكوت)
- Al Mazyunah (المزيونة)
- Muqshin (مقشن)
- Shalim & Hallaniyat Islands (شليم وجزر الحلانيات)
- Sadah (سدح)

**Musandam Governorate:**
- Khasab (خصب)
- Dibba (دبا)
- Bukha (بخا)
- Madha (مدحاء)

**Al Buraimi Governorate:**
- Al Buraimi (البريمي)
- Mahdha (ومضة)
- Al Sunainah (السنينة)

**Ad Dakhiliyah Governorate:**
- Nizwa (نزوى)
- Samail (سمائل)
- Bahla (بهلاء)
- Adam (أدم)
- Al Hamra (الحمراء)
- Manah (منح)
- Izki (إزكي)
- Bidbid (بِدبد)
- Jebel Akhdar (الجبل الأخضر)

**Al Batinah North Governorate:**
- Sohar (صحار)
- Shinas (شناص)
- Liwa (لوى)
- Saham (صحم)
- Al Khaburah (الخابورة)
- Al Suwaiq (السويق)

**Al Batinah South Governorate:**
- Rustaq (الرستاق)
- Al Awabi (العوابي)
- Nakhl (نخل)
- Wadi Al Maawil (وادي المعاول)
- Barka (بركاء)
- Al Musannah (المصنعة)

**Ash Sharqiyah North Governorate:**
- Ibra (إبراء)
- Mudhaibi (المضيبي)
- Bidiyah (بدية)
- Al Qabil (القابل)
- Wadi Bani Khalid (وادي بني خالد)
- Demaa Wa Al Tayin (دماء والطائيين)

**Ash Sharqiyah South Governorate:**
- Sur (صور)
- Al Kamil Wa Al Wafi (الكامل والوافي)
- Jaalan Bani Bu Hasan (جعلان بني بو حسن)
- Jaalan Bani Bu Ali (جعلان بني بو علي)
- Masirah (مصيرة)

**Ad Dhahirah Governorate:**
- Ibri (عبري)
- Yanqul (ينقل)
- Dank (ضنك)

**Al Wusta Governorate:**
- Haima (هيماء)
- Mahout (محوت)
- Duqm (الدقم)
- Al Jazer (الجازر)

## Important Implementation Notes

1. **Token Storage:**
   - Store JWT tokens securely on the client side
   - Never store sensitive tokens in localStorage for production applications
   - Consider using HTTP-only cookies for the refresh token

2. **Error Handling:**
   - Implement proper error handling for all API responses
   - Display user-friendly error messages based on the error codes received
   - Validate form inputs on the frontend before submission to improve user experience

3. **Field Dependencies:**
   - The wilayat field is dependent on the governorate selection
   - Frontend should dynamically update available wilayat options based on the selected governorate

4. **Phone Format:**
   - Ensure phone numbers are always formatted as +968XXXXXXXX
   - Consider implementing a phone input mask on the frontend to guide users

5. **Authorization:**
   - For protected endpoints, always include the access token in the Authorization header
   - Format: `Authorization: Bearer {access_token}`
   - Handle token expiration by implementing automatic token refresh using the refresh token
