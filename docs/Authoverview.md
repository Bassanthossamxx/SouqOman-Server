# Authentication System Overview

This document outlines the authentication system for the project, detailing the available endpoints and the user model.

## Endpoints

- **Register**: Allows new users to sign up by providing required personal information. On successful registration, users receive access and refresh tokens. OTP verification via Meta WP is planned for future implementation.
- **Login**: Authenticates users using their phone number and password, returning access and refresh tokens upon success.
- **Logout**: Invalidates the current access token, effectively logging the user out.
- **User Details**: Retrieves user information based on the provided access token.

## User Model

The user model includes the following fields:
1. Full name (Arabic)
2. Full name (English)
3. Email address
4. Oman phone number
5. Government (with associated Wilayat)
6. Password

## Notes

- JWT-based authentication is used for issuing and validating access and refresh tokens.
- Future enhancements will include OTP verification during registration.
