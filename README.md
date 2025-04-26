# startup-go-backend

Backend repo for team "Startup Go" @ HackDKU25

## API Reference

### Authentication Endpoints

#### User Registration

```http
POST /api/users/register/
Content-Type: application/json
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

**Note:** After successful registration, you should call `POST /api/users/profile/` to initialize the user's profile!

#### User Login

```http
POST /api/users/login/
Content-Type: application/json
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
Content-Type: application/json
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

### Profile Management Endpoints

#### Initialize User Profile

```http
POST /api/users/profile/
Content-Type: application/json
Authorization: Bearer <access_token>
```

Initialize a new user profile. This endpoint must be called after user registration to set up the initial profile information.

**Request Body:**

```json
{
    "first_name": "Test",
    "last_name": "User",
    "profile": {
        "industry": "Technology",
        "role": "Software Engineer",
        "location": "New York, USA",
        "skills": "Python, Django, React, AWS",
        "goals": "Build innovative solutions and contribute to open source",
        "website": "https://example.com",
        "social_links": {
            "github": "https://github.com/testuser",
            "linkedin": "https://linkedin.com/in/testuser"
        },
        "projects": ["project-id-1", "project-id-2"]
    }
}
```

**Response (201 Created):**

```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "profile": {
        "bio": "",
        "avatar": null,
        "industry": "Technology",
        "role": "Software Engineer",
        "location": "New York, USA",
        "skills": "Python, Django, React, AWS",
        "goals": "Build innovative solutions and contribute to open source",
        "website": "https://example.com",
        "social_links": {
            "github": "https://github.com/testuser",
            "linkedin": "https://linkedin.com/in/testuser"
        },
        "projects": ["project-id-1", "project-id-2"]
    }
}
```

**Error Response (400 Bad Request):**

```json
{
    "error": "Profile already exists"
}
```

**Error Response (400 Bad Request - Validation Error):**

```json
{
    "skills": ["Skills description is too long."],
    "goals": ["Goals description is too long."]
}
```

#### Get User Profile

```http
GET /api/users/profile/
Authorization: Bearer <access_token>
```

Get the current user's profile information.

**Response (200 OK):**

```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "profile": {
        "bio": "Software Developer",
        "avatar": "https://example.com/avatars/user1.jpg",
        "industry": "Technology",
        "role": "Software Engineer",
        "location": "New York, USA",
        "skills": "Python, Django, React, AWS",
        "goals": "Build innovative solutions and contribute to open source",
        "website": "https://example.com",
        "social_links": {
            "github": "https://github.com/testuser",
            "linkedin": "https://linkedin.com/in/testuser"
        },
        "projects": ["project-id-1", "project-id-2"]
    }
}
```

#### Update User Profile

```http
PUT /api/users/profile/
Content-Type: application/json
Authorization: Bearer <access_token>
```

Update the current user's profile information.

**Request Body:**

```json
{
    "first_name": "Updated",
    "last_name": "Name",
    "profile": {
        "bio": "Updated bio",
        "industry": "FinTech",
        "role": "Full Stack Developer",
        "location": "San Francisco, USA",
        "skills": "Python, Django, React, AWS, Docker",
        "goals": "Lead development of innovative fintech solutions",
        "website": "https://updated.com",
        "social_links": {
            "github": "https://github.com/updated",
            "linkedin": "https://linkedin.com/in/updated"
        },
        "projects": ["project-id-1", "project-id-2"]
    }
}
```

**Response (200 OK):**

```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "first_name": "Updated",
    "last_name": "Name",
    "profile": {
        "bio": "Updated bio",
        "avatar": "https://example.com/avatars/user1.jpg",
        "industry": "FinTech",
        "role": "Full Stack Developer",
        "location": "San Francisco, USA",
        "skills": "Python, Django, React, AWS, Docker",
        "goals": "Lead development of innovative fintech solutions",
        "website": "https://updated.com",
        "social_links": {
            "github": "https://github.com/updated",
            "linkedin": "https://linkedin.com/in/updated"
        },
        "projects": ["project-id-1", "project-id-2"]
    }
}
```

#### Upload Profile Avatar

```http
POST /api/users/profile/avatar/
Content-Type: multipart/form-data
Authorization: Bearer <access_token>
```

Upload or update the user's profile avatar.

**Request Body:**

```
avatar: <file>
```

**Response (200 OK):**

```json
{
    "avatar": "https://example.com/avatars/user1.jpg"
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
