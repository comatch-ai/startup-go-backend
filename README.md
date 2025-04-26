# startup-go-backend
Backend repo for team "Startup Go" @ HackDKU25

## API Reference

### Authentication Endpoints

#### User Registration
```http
POST /api/users/register/
```

Register a new user in the system.

**Request Body:**
```json
{
    "username": "testuser",
    "email": "test@example.com",
    "password": "your_password",
    "password2": "your_password",
    "first_name": "Test",
    "last_name": "User"
}
```

**Response (201 Created):**
```json
{
    "user": {
        "username": "testuser",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (400 Bad Request):**
```json
{
    "username": ["This field is required."],
    "password": ["This field is required."],
    "password2": ["This field is required."]
}
```

#### User Login
```http
POST /api/users/login/
```

Authenticate a user and get JWT tokens.

**Request Body:**
```json
{
    "username": "testuser",
    "password": "your_password"
}
```

**Response (200 OK):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Error Response (401 Unauthorized):**
```json
{
    "error": "Invalid credentials"
}
```

#### Token Refresh
```http
POST /api/token/refresh/
```

Refresh the access token using a refresh token.

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Authentication

All protected endpoints require JWT authentication. Include the access token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Token Lifetime

- Access Token: 60 minutes
- Refresh Token: 24 hours
