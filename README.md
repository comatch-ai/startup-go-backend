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

#### Get User Profile by Username

```http
GET /api/users/<username>/profile/
Authorization: Bearer <access_token>
```

Get a user's profile by their username.

**URL Parameters:**
- `username`: The username of the user whose profile to retrieve

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

**Error Response (404 Not Found):**

```json
{
    "error": "User not found"
}
```

**Error Response (401 Unauthorized):**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### List All User Profiles

```http
GET /api/users/profiles/
Authorization: Bearer <access_token>
```

Get a list of all user profiles with optional filtering.

**Query Parameters:**
- `industry`: Filter by industry (e.g., Technology, Healthcare)
- `role`: Filter by role (e.g., Software Engineer, Doctor)
- `location`: Filter by location (e.g., New York, San Francisco)
- `skills`: Filter by skills (comma-separated, e.g., Python,Django,React)
- `startup_stage`: Filter by startup stage (e.g., ideation, mvp)

**Response (200 OK):**

```json
[
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
    },
    {
        "id": 2,
        "username": "otheruser",
        "email": "other@example.com",
        "first_name": "Other",
        "last_name": "User",
        "profile": {
            "bio": "Healthcare Professional",
            "avatar": "https://example.com/avatars/user2.jpg",
            "industry": "Healthcare",
            "role": "Doctor",
            "location": "Boston, USA",
            "skills": "Medicine, Research",
            "goals": "Improve healthcare through technology",
            "website": "https://other.com",
            "social_links": {
                "github": "https://github.com/otheruser",
                "linkedin": "https://linkedin.com/in/otheruser"
            },
            "projects": []
        }
    }
]
```

**Error Response (401 Unauthorized):**

```json
{
    "detail": "Authentication credentials were not provided."
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

### Project Management Endpoints

#### Create Project

```http
POST /api/projects/
Content-Type: application/json
Authorization: Bearer <access_token>
```

Create a new project.

**Request Body:**

```json
{
    "title": "AI-Powered Task Manager",
    "tagline": "Revolutionizing personal productivity through AI",
    "description": "An intelligent task management system that uses AI to prioritize and organize tasks",
    "industry": "Technology",
    "stage": "ideation",
    "startup_type": "B2C",
    "business_model": ["Freemium", "Subscription"],
    "team_size": 3,
    "website": "https://example.com",
    "social_links": {
        "github": "https://github.com/project",
        "linkedin": "https://linkedin.com/company/project"
    },
    "equity": 25.50,
    "funding": "invested"
}
```

**Field Descriptions:**
- `title`: Project title (required)
- `tagline`: Short project description (required)
- `description`: Detailed project description (required)
- `industry`: Project industry (required)
- `stage`: Project development stage (required)
  - Choices: pre_idea, ideation, prototype, mvp, pre_seed, seed, scaling, established, expansion, pivot
- `startup_type`: Type of startup (required)
  - Choices: B2B, B2C, B2B2C, C2C, B2G, G2C, Others
- `business_model`: List of business models (required)
  - Choices: Freemium, Subscription, Marketplace, SaaS, E-commerce, Enterprise, Advertising, Transaction, Licensing, Direct Sales, Others
- `team_size`: Number of team members (required, minimum: 1)
- `website`: Project website URL (optional)
- `social_links`: Dictionary of social media links (optional)
- `equity`: Equity percentage (required, 0-100 with 2 decimal places)
- `funding`: Funding type (required)
  - Choices: self_funded, loan, invested, sponsored, Others

**Response (201 Created):**

```json
{
    "id": "project-id-1",
    "title": "AI-Powered Task Manager",
    "tagline": "Revolutionizing personal productivity through AI",
    "description": "An intelligent task management system that uses AI to prioritize and organize tasks",
    "industry": "Technology",
    "stage": "ideation",
    "startup_type": "B2C",
    "business_model": ["Freemium", "Subscription"],
    "team_size": 3,
    "website": "https://example.com",
    "social_links": {
        "github": "https://github.com/project",
        "linkedin": "https://linkedin.com/company/project"
    },
    "equity": "25.50",
    "funding": "invested",
    "created_by": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    },
    "created_at": "2024-02-20T10:00:00Z",
    "updated_at": "2024-02-20T10:00:00Z"
}
```

**Error Response (400 Bad Request - Validation Error):**

```json
{
    "equity": ["Equity must be between 0 and 100."],
    "funding": ["Invalid funding type. Must be one of: self_funded, loan, invested, sponsored, Others"],
    "team_size": ["Team size must be at least 1."]
}
```

#### Get Project Details

```http
GET /api/projects/{project_id}/
Authorization: Bearer <access_token>
```

Get detailed information about a specific project.

**Response (200 OK):**

```json
{
    "id": "project-id-1",
    "title": "AI-Powered Task Manager",
    "tagline": "Revolutionizing personal productivity through AI",
    "description": "An intelligent task management system that uses AI to prioritize and organize tasks",
    "industry": "Technology",
    "stage": "ideation",
    "startup_type": "B2C",
    "business_model": ["Freemium", "Subscription"],
    "team_size": 3,
    "website": "https://example.com",
    "social_links": {
        "github": "https://github.com/project",
        "linkedin": "https://linkedin.com/company/project"
    },
    "equity": "25.50",
    "funding": "invested",
    "created_by": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    },
    "created_at": "2024-02-20T10:00:00Z",
    "updated_at": "2024-02-20T10:00:00Z"
}
```

#### List Projects

```http
GET /api/projects/
Authorization: Bearer <access_token>
```

Get a list of all projects with optional filtering.

**Query Parameters:**

- `industry`: Filter by industry
- `stage`: Filter by project stage
- `startup_type`: Filter by startup type (B2B, B2C, etc.)
- `business_model`: Filter by business model
- `funding`: Filter by funding type (self_funded, loan, invested, sponsored, Others)
- `page`: Page number for pagination
- `page_size`: Number of items per page

**Response (200 OK):**

```json
{
    "count": 100,
    "next": "http://api.example.com/projects/?page=2",
    "previous": null,
    "results": [
        {
            "id": "project-id-1",
            "title": "AI-Powered Task Manager",
            "tagline": "Revolutionizing personal productivity through AI",
            "description": "An intelligent task management system...",
            "industry": "Technology",
            "stage": "ideation",
            "startup_type": "B2C",
            "business_model": ["Freemium", "Subscription"],
            "team_size": 3,
            "website": "https://example.com",
            "equity": "25.50",
            "funding": "invested",
            "created_at": "2024-02-20T10:00:00Z"
        },
        // ... more projects
    ]
}
```

#### Update Project

```http
PUT /api/projects/{project_id}/
Content-Type: application/json
Authorization: Bearer <access_token>
```

Update an existing project.

**Request Body:**

```json
{
    "title": "Updated Project Title",
    "tagline": "Updated tagline",
    "description": "Updated project description",
    "stage": "prototype",
    "startup_type": "B2B2C",
    "business_model": ["Subscription", "Enterprise"],
    "team_size": 4,
    "website": "https://updated.com",
    "social_links": {
        "github": "https://github.com/updated",
        "linkedin": "https://linkedin.com/company/updated"
    },
    "equity": 30.00,
    "funding": "sponsored"
}
```

**Response (200 OK):**

```json
{
    "id": "project-id-1",
    "title": "Updated Project Title",
    "tagline": "Updated tagline",
    "description": "Updated project description",
    "industry": "Technology",
    "stage": "prototype",
    "startup_type": "B2B2C",
    "business_model": ["Subscription", "Enterprise"],
    "team_size": 4,
    "website": "https://updated.com",
    "social_links": {
        "github": "https://github.com/updated",
        "linkedin": "https://linkedin.com/company/updated"
    },
    "equity": "30.00",
    "funding": "sponsored",
    "created_by": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com"
    },
    "created_at": "2024-02-20T10:00:00Z",
    "updated_at": "2024-02-20T11:00:00Z"
}
```

#### Delete Project

```http
DELETE /api/projects/{project_id}/
Authorization: Bearer <access_token>
```

Delete a project.

**Response (204 No Content)**

### Recommendation Endpoints

#### Get User Recommendations

```http
GET /api/recommendations/
Authorization: Bearer <access_token>
```

Get personalized user recommendations based on profile similarity.

**Description:**
This endpoint recommends users based on the following criteria:
- Industry match
- Role match
- Location match
- Skills overlap
- Goals similarity

The recommendations are scored and sorted by similarity score.

**Response (200 OK):**

```json
[
    {
        "username": "recommendeduser",
        "email": "recommended@example.com",
        "first_name": "Recommended",
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
                "github": "https://github.com/recommendeduser",
                "linkedin": "https://linkedin.com/in/recommendeduser"
            },
            "projects": ["project-id-1", "project-id-2"]
        },
        "score": 4
    },
    // ... more recommendations
]
```

**Error Response (404 Not Found):**

```json
{
    "error": "Profile not found"
}
```

**Error Response (401 Unauthorized):**

```json
{
    "detail": "Authentication credentials were not provided."
}
```

**Note:** The score represents the number of matching criteria between the current user and the recommended user. Higher scores indicate better matches.

### Authentication

All protected endpoints require JWT authentication. Include the access token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Token Lifetime

- Access Token: 60 minutes
- Refresh Token: 24 hours

### Friend Management Endpoints

#### Add a Friend

```http
POST /api/friends/add/
Authorization: Bearer <access_token>
Content-Type: application/json
```

Add a user to your friends list by their user ID.

**Request Body:**
```json
{
  "friend_id": 2
}
```

**Response (200 OK):**
```json
{
  "success": "User frienduser added as a friend."
}
```

**Error Responses:**
- `400 Bad Request` if already friends or missing friend_id.
- `404 Not Found` if the user does not exist.
- `401 Unauthorized` if not authenticated.

---

#### Remove a Friend

```http
POST /api/friends/remove/
Authorization: Bearer <access_token>
Content-Type: application/json
```

Remove a user from your friends list by their user ID.

**Request Body:**
```json
{
  "friend_id": 2
}
```

**Response (200 OK):**
```json
{
  "success": "User 2 removed from friends."
}
```

**Error Responses:**
- `400 Bad Request` if the user is not in your friends list or missing friend_id.
- `401 Unauthorized` if not authenticated.

---

#### Get Mutual Friends

```http
GET /api/friends/match/
Authorization: Bearer <access_token>
```

Returns a list of user IDs who are mutual friends (i.e., both users have each other in their friends list).

**Response (200 OK):**
```json
{
  "mutual_friends": [2, 5, 7]
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Note:**
- Only users who are in your friends list and also have you in their friends list will be returned.
