# Authentication API Documentation

This document provides detailed information about the authentication endpoints for SouqOman platform. It covers OTP verification, user registration, login, logout, user details, and token management processes, including request parameters, validation rules, error scenarios, and response formats.

## Authentication Endpoints
base url for all endpoints: `/api/auth/`

## Rate Limiting
To protect the platform from abuse, authentication endpoints are rate limited. If a client exceeds the limits below, the API responds with `429 Too Many Requests`.

Current limits:
- `POST /api/auth/send/otp/`: 20 requests per hour (per phone number)
- `POST /api/auth/verify/otp/`: 10 requests per hour (per phone number)
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

## OTP Flow (Phone Verification)

Before registering, users must verify their phone number using OTP (One-Time Password). This is a two-step process:

1. **Send OTP**: Request an OTP code to be sent to the phone number
2. **Verify OTP**: Confirm the OTP code received via WP or SMS if WP is not available

### 1. Send OTP

Initiates the OTP verification process by sending a one-time password to the provided phone number via WP message /SMS.

**Endpoint:** `send/otp/`

**Method:** `POST`

**Content-Type:** `application/json`

**Authentication:** Not required

#### Request Body

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|-----------------|
| phone | string | Yes | User's phone number | Must be a valid Omani phone number format (e.g., +968XXXXXXXX ) |

#### Example Request

```json
{
  "phone": "+96891234567"
}
```

#### Success Response (200 OK)

```json
{
  "message": "OTP sent successfully"
}
```

Notes:
- The OTP code is sent via WP/SMS to the provided phone number
- The OTP is valid for a limited time (typically 3 minutes)
- Users must wait 60 seconds before requesting a new OTP for the same phone number

#### Error Responses

**400 Bad Request - Phone Already Registered**

```json
{
  "error": "Phone number already registered. Please login instead."
}
```

**429 Too Many Requests - OTP Already Sent**

If the user tries to send OTP again within 60 seconds:

```json
{
  "error": "OTP already sent. Please wait 60 seconds or use resend OTP endpoint."
}
```

**400 Bad Request - Missing Phone**

```json
{
  "phone": ["This field is required."]
}
```

**400 Bad Request - External Service Error**

If the OTP service (Akedly) fails:

```json
{
  "error": "Akedly OTP error: [error message from service]"
}
```

**400 Bad Request - Network Error**

If there's a DNS or connection issue:

```json
{
  "error": "HTTPSConnectionPool(host='api.akedly.com', port=443): Max retries exceeded with url: /otp (Caused by NameResolutionError..."
}
```

#### Resending OTP

To resend an OTP, simply call the same endpoint again after waiting 60 seconds. There is no separate resend endpoint.

**Example:**
1. First request: OTP sent immediately
2. Second request within 60 seconds: Returns 429 error
3. Request after 60+ seconds: Sends new OTP successfully

---

### 2. Verify OTP

Verifies the OTP code sent to the user's phone number. This step must be completed before registration.

**Endpoint:** `verify/otp/`

**Method:** `POST`

**Content-Type:** `application/json`

**Authentication:** Not required

#### Request Body

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|-----------------|
| phone | string | Yes | User's phone number (same as used in send OTP) | Must match the phone number used to request OTP |
| otp | string | Yes | The OTP code received via SMS | Typically 4-6 digits |

#### Example Request

```json
{
  "phone": "+96891234567",
  "otp": "123456"
}
```

#### Success Response (200 OK)

```json
{
  "message": "Phone verified successfully."
}
```

Notes:
- Once verified, the phone number is marked as verified in the system
- The verification is temporary and should be followed by registration
- The verified status allows the user to proceed with registration

#### Error Responses

**404 Not Found - No OTP Request Found**

If no OTP was sent to this phone number:

```json
{
  "detail": "Not found."
}
```

**400 Bad Request - Invalid OTP**

```json
{
  "error": "OTP verification failed"
}
```

or

```json
{
  "error": "Invalid or expired OTP code"
}
```

**400 Bad Request - Missing Fields**

```json
{
  "phone": ["This field is required."],
  "otp": ["This field is required."]
}
```

**400 Bad Request - OTP Service Error**

```json
{
  "error": "Request error: [error details]"
}
```

---

### 3. User Registration

Registers a new user in the system and automatically authenticates them (issues JWT access & refresh tokens). **Phone number must be verified via OTP before registration.**

**Endpoint:** `register/`

**Method:** `POST`

**Content-Type:** `application/json`

**Authentication:** Not required

#### Request Body

| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|-----------------|
| phone | string | Yes | User's phone number (must be verified) | Must be verified via OTP first; must follow Omani format: +968XXXXXXXX |
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
  "phone": "+96891234567",
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
- The user is fully authenticated immediately after registration
- Store the tokens securely (prefer HTTP-only cookies or secure storage)
- The phone verification record is deleted after successful registration
- No need to call the login endpoint after registration

#### Error Responses

**400 Bad Request - Phone Not Verified**

If the phone number was not verified via OTP:

```json
{
  "error": "Phone not verified. Please verify before registration."
}
```

**400 Bad Request - Phone Number Validation**

```json
{
  "phone": ["Phone must follow Omani format: +968XXXXXXXX"]
}
```

or if phone is already registered:

```json
{
  "phone": ["User with this phone already exists."]
}
```

**400 Bad Request - Email Validation**

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

**400 Bad Request - Password Validation**

```json
{
  "password": [
    "This password is too short. It must contain at least 8 characters.",
    "This password is too common.",
    "This password is entirely numeric."
  ]
}
```

**400 Bad Request - Password Mismatch**

```json
{
  "passwords": ["Passwords must match."]
}
```

**400 Bad Request - Name Validation**

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

**400 Bad Request - Governorate/Wilayat Validation**

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

**429 Too Many Requests**

```json
{
  "detail": "Request was throttled. Expected available in 59 minutes."
}
```

---

### 4. User Login

Authenticates a user and provides access tokens.

**Endpoint:** `login/`

**Method:** `POST`

**Content-Type:** `application/json`

**Authentication:** Not required

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| phone | string | Yes | User's phone number in format +968XXXXXXXX|
| password | string | Yes | User's password |

#### Example Request

```json
{
  "phone": "+96891234567",
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

#### Error Responses

**400 Bad Request - Invalid Credentials**

```json
{
  "non_field_errors": ["Invalid phone or password."]
}
```

**400 Bad Request - Missing Fields**

```json
{
  "phone": ["This field is required."],
  "password": ["This field is required."]
}
```

**429 Too Many Requests**

```json
{
  "detail": "Request was throttled. Expected available in 30 seconds."
}
```

---

### 5. User Logout

Logs out a user by blacklisting their refresh token.

**Endpoint:** `logout/`

**Method:** `POST`

**Content-Type:** `application/json`

**Authentication:** Requires a valid access token in the Authorization header.

**Authorization Header:** `Authorization: Bearer {access_token}`

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

**Additional Success (200 OK - idempotent):**

```json
{
  "detail": "Already logged out."
}
```

Notes:
- Logout is idempotent. If the same refresh token is sent again after being blacklisted, the endpoint returns 200 OK with `"detail": "Already logged out."`
- After logout, both the access and refresh tokens are invalid

#### Error Responses

**400 Bad Request - Missing Refresh Token**

```json
{
  "error": "Refresh token is required."
}
```

**400 Bad Request - Invalid Token**

```json
{
  "error": "Invalid or expired refresh token."
}
```

**401 Unauthorized - No Access Token**

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

---

### 6. User Details

Retrieves the authenticated user's profile details.

**Endpoint:** `me/`

**Method:** `GET`

**Authentication:** Requires a valid access token in the Authorization header.

**Authorization Header:** `Authorization: Bearer {access_token}`

#### Success Response (200 OK)

```json
{
  "id": 1,
  "phone": "96891234567",
  "email": "user@example.com",
  "full_name_ar": "محمد أحمد",
  "full_name_en": "Mohammed Ahmed",
  "governorate": "Muscat",
  "wilayat": "Al Seeb"
}
```

#### Error Responses

**401 Unauthorized - No Access Token**

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**401 Unauthorized - Invalid/Expired Token**

```json
{
  "detail": "Given token not valid for any token type",
  "code": "token_not_valid",
  "messages": [
    {
      "token_class": "AccessToken",
      "token_type": "access",
      "message": "Token is invalid or expired"
    }
  ]
}
```

---

### 7. JWT Token Obtain

Alternative endpoint to obtain JWT tokens using standard JWT authentication.

**Endpoint:** `token/`

**Method:** `POST`

**Content-Type:** `application/json`

**Authentication:** Not required

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | User's phone number (used as username) |
| password | string | Yes | User's password |

#### Example Request

```json
{
  "username": "+96891234567",
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

#### Error Responses

**401 Unauthorized - Invalid Credentials**

```json
{
  "detail": "No active account found with the given credentials"
}
```

**429 Too Many Requests**

```json
{
  "detail": "Request was throttled. Expected available in 30 seconds."
}
```

---

### 8. JWT Token Refresh

Obtain a new access token using a valid refresh token.

**Endpoint:** `token/refresh/`

**Method:** `POST`

**Content-Type:** `application/json`

**Authentication:** Not required

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

#### Error Responses

**401 Unauthorized - Invalid/Expired Token**

```json
{
  "detail": "Token is invalid or expired",
  "code": "token_not_valid"
}
```

**429 Too Many Requests**

```json
{
  "detail": "Request was throttled. Expected available in 30 seconds."
}
```

---

## Complete Authentication Flow

###  User Registration Flow

1. **Send OTP**: Client sends phone number to `send/otp/`
   ```json
   POST /api/auth/send/otp/
   {
     "phone": "+96891234567"
   }
   ```
   Response: `{"message": "OTP sent successfully"}`

2. **Verify OTP**: User receives SMS with OTP code and submits it
   ```json
   POST /api/auth/verify/otp/
   {
     "phone": "+96891234567",
     "otp": "123456"
   }
   ```
   Response: `{"message": "Phone verified successfully."}`

3. **Register**: Client sends complete registration data
   ```json
   POST /api/auth/register/
   {
     "phone": "+96891234567",
     "email": "user@example.com",
     "password": "SecurePassword123",
     "password2": "SecurePassword123",
     "full_name_ar": "محمد أحمد",
     "full_name_en": "Mohammed Ahmed",
     "governorate": "Muscat",
     "wilayat": "Al Seeb"
   }
   ```
   Response: Returns both `access` and `refresh` tokens (auto-login)

4. **Store Tokens**: Save the tokens securely on the client

###  User Login Flow

1. **Login**: Client sends credentials to `login/`
   ```json
   POST /api/auth/login/
   {
     "phone": "+96891234567",
     "password": "SecurePassword123"
   }
   ```
   Response: Returns both `access` and `refresh` tokens

2. **Store Tokens**: Save the tokens securely

### Authenticated Requests

For all protected endpoints, include the access token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Example:
```
GET /api/auth/me/
Headers:
  Authorization: Bearer {access_token}
```

### Token Refresh Flow

When the access token expires (typically after 5-15 minutes):

1. **Refresh Token**: Send refresh token to get new access token
   ```json
   POST /api/auth/token/refresh/
   {
     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   }
   ```
   Response: Returns new `access` token

2. **Update Stored Token**: Replace old access token with new one

### Logout Flow

1. **Logout**: Send refresh token to invalidate session
   ```json
   POST /api/auth/logout/
   Headers:
     Authorization: Bearer {access_token}
   Body:
   {
     "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
   }
   ```
   Response: `{"detail": "Successfully logged out."}`

2. **Clear Tokens**: Remove all stored tokens from client

---

## OTP Resend Logic

The platform implements intelligent OTP resend logic to prevent abuse:

- **First Request**: OTP is sent immediately
- **Within 60 seconds**: Returns 429 error: `"OTP already sent. Please wait 60 seconds or use resend OTP endpoint."`
- **After 60 seconds**: User can call the same `send/otp/` endpoint again to receive a new OTP
- **No separate resend endpoint**: Simply retry the `send/otp/` endpoint after the cooldown period

Example Timeline:
```
00:00 - User requests OTP → OTP sent successfully
00:30 - User requests OTP again → 429 Error (wait 30 more seconds)
01:05 - User requests OTP again → New OTP sent successfully
```

---

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
- Bidbid (بدبد)
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

---

## Important Implementation Notes

1. **Phone Verification is Mandatory:**
   - All new users must verify their phone number via OTP before registration
   - Registration will fail if the phone number is not verified
   - Phone verification is temporary and expires after successful registration

2. **OTP Rate Limiting:**
   - Users must wait 60 seconds between OTP requests for the same phone number
   - No separate resend endpoint - use the same `send/otp/` endpoint after cooldown
   - Prevents SMS spam and abuse

3. **Phone Number Validation:**
   - Phone numbers already registered cannot request OTP
   - The system will return an error directing users to login instead
   - Supports format: `+968XXXXXXXX`

4. **Token Storage:**
   - Store JWT tokens securely on the client side
   - Never store sensitive tokens in localStorage for production applications
   - Consider using HTTP-only cookies for the refresh token
   - Access tokens typically expire in 6 hours
   - Refresh tokens typically expire in 30 days

5. **Error Handling:**
   - Implement proper error handling for all API responses
   - Display user-friendly error messages based on the error codes received
   - Validate form inputs on the frontend before submission to improve user experience
   - Handle OTP service failures gracefully with retry mechanisms

6. **Field Dependencies:**
   - The wilayat field is dependent on the governorate selection
   - Frontend should dynamically update available wilayat options based on the selected governorate
   - Validate governorate/wilayat combinations on both frontend and backend

7. **Phone Format:**
   - Ensure phone numbers are always formatted consistently
   - Consider implementing a phone input mask on the frontend to guide users
   - Backend accepts both `+968XXXXXXXX`` format

8. **Authorization:**
   - For protected endpoints, always include the access token in the Authorization header
   - Format: `Authorization: Bearer {access_token}`
   - Handle token expiration by implementing automatic token refresh using the refresh token
   - Redirect to login page if refresh token is also expired

9. **OTP Service Integration:**
   - The platform uses Akedly service for OTP delivery
   - Network issues or service downtime may affect OTP delivery
   - Implement proper error handling and user feedback for service failures
   - Consider implementing fallback mechanisms for critical flows

10. **Security Best Practices:**
   - Always use HTTPS in production
   - Implement CSRF protection for state-changing operations
   - Rate limit authentication endpoints to prevent brute force attacks
   - Log authentication attempts for security monitoring
   - Implement account lockout after multiple failed login attempts
