# Proxam AI — Technical Stack

## 1. Document Purpose

This document defines the technologies, tools, architecture, and implementation choices for **Proxam AI**, an online examination platform with AI-assisted proctoring.

The selected stack is designed to be:

* Beginner-friendly enough to learn and implement
* Suitable for a serious college major project
* Compatible with a React frontend
* Suitable for browser-based AI monitoring
* Extendable for advanced Python-based AI features
* Simple enough to maintain
* Appropriate for the current simplified application flow
* Free from unnecessary enterprise-level complexity

The first version will focus on:

* User authentication
* Role-based dashboards
* Teacher-created MCQ tests
* Backend-generated test codes
* Student test-code access
* Timed examinations
* Automatic result calculation
* Basic browser-based proctoring
* Proctoring event storage
* Teacher attempt and result review
* Basic admin management

---

## 2. Finalized Application Roles

The system will support exactly three roles:

1. Student
2. Teacher
3. Admin

### Student

Students can:

* Register and log in
* Enter a test code
* View test details
* Complete the pre-exam system check
* Attempt an examination
* Submit answers
* View results
* View examination history
* Manage their profile

### Teacher

Teachers can:

* Register and log in
* View their dashboard
* Create MCQ tests
* Add questions and answer options
* Preview tests
* Publish or create tests
* Receive a unique test code
* View test details
* View student attempts and results
* Review proctoring events
* Manage their profile

### Admin

Admins can:

* View system overview
* Manage users
* View tests
* View test attempts
* Review proctoring alerts
* Manage their profile

Advanced administrative features are not required in the first version.

---

## 3. Technology Stack Overview

| Layer                        | Technology                                         |
| ---------------------------- | -------------------------------------------------- |
| Frontend framework           | React                                              |
| Frontend build tool          | Vite                                               |
| Frontend language            | JavaScript                                         |
| Styling                      | Tailwind CSS + CSS variables                       |
| Routing                      | React Router                                       |
| Backend language             | Python                                             |
| Backend framework            | FastAPI                                            |
| Backend server               | Uvicorn                                            |
| API validation               | Pydantic                                           |
| Database                     | PostgreSQL                                         |
| Database models and ORM      | SQLModel                                           |
| Database migrations          | Alembic                                            |
| Authentication               | JWT with secure HTTP-only cookies                  |
| Password hashing             | pwdlib with Argon2                                 |
| API communication            | REST API                                           |
| Browser face monitoring      | MediaPipe                                          |
| Webcam and microphone access | MediaDevices API                                   |
| Fullscreen monitoring        | Fullscreen API                                     |
| Tab-switch monitoring        | Page Visibility API                                |
| Browser-side monitoring      | JavaScript                                         |
| Advanced AI later            | Python, OpenCV, and suitable face-analysis modules |
| Backend testing              | Pytest                                             |
| API testing                  | HTTPX                                              |
| Frontend testing later       | Vitest                                             |
| API documentation            | FastAPI Swagger/OpenAPI                            |
| Frontend deployment          | Vercel                                             |
| Backend deployment           | Render or Railway                                  |
| Database hosting             | Neon or Supabase                                   |
| Version control              | Git and GitHub                                     |

---

## 4. Frontend Stack

### 4.1 React

React will be used to build the Proxam AI frontend.

It will manage:

* Landing page
* Authentication screens
* Student dashboard
* Teacher dashboard
* Admin dashboard
* Enter Test Code screen
* Test creation screens
* Test details
* Pre-exam system check
* Active examination interface
* Result pages
* Examination history
* Proctoring status components
* Profile pages
* Error and unauthorized screens

React is suitable because Proxam AI contains multiple interactive screens, protected routes, forms, timers, question navigation, and role-based dashboards.

---

### 4.2 Vite

Vite will be used as the frontend development and build tool.

It will provide:

* Fast development server
* Fast hot module replacement
* Production build support
* Simple React project setup
* Easy environment-variable configuration

The project will use Vite instead of Create React App.

Example setup:

```bash
npm create vite@latest frontend
```

The exact command may change depending on the final project setup.

---

### 4.3 JavaScript

JavaScript will be used instead of TypeScript for the initial version.

Reasons:

* The current frontend learning path is JavaScript and React.
* JavaScript reduces the number of new concepts.
* It allows faster implementation.
* It is sufficient for the first version of the project.
* TypeScript can be introduced later if the application is expanded.

The codebase should still follow:

* Clear naming conventions
* Reusable components
* Consistent folder organization
* Small and understandable functions
* Separation of UI and API logic
* Consistent error handling

---

### 4.4 Tailwind CSS and CSS Variables

Tailwind CSS will be used for most interface styling.

CSS variables will be used for:

* Light and dark themes
* Background colors
* Surface colors
* Text colors
* Pastel accent colors
* Border colors
* Status colors
* Typography values
* Border radii
* Spacing tokens
* Focus states

The design should follow the pastel education-dashboard theme defined in `DESIGN.md`.

The interface should use:

* Warm off-white backgrounds
* White surfaces
* Soft mint
* Lavender
* Peach
* Pink
* Pale blue
* Rounded cards
* Pill-shaped buttons
* Subtle shadows

---

### 4.5 React Router

React Router will manage frontend navigation.

It will support routes for:

* Public pages
* Login
* Registration
* Forgot Password
* Reset Password
* Student dashboard
* Enter Test Code
* Test details
* Pre-exam system check
* Active examination
* Results
* Examination history
* Teacher dashboard
* Test records
* Create Test
* Test preview
* Test details
* Attempts and results
* Admin dashboard
* User management
* Test management
* Proctoring alerts
* Profile pages
* Unauthorized page
* Not Found page

Protected routes will restrict access based on:

* Authentication status
* User role
* Test ownership
* Attempt ownership
* Examination state

---

## 5. Backend Stack

### 5.1 Python

Python will be used for backend development.

Python is selected because:

* It supports the future AI and machine-learning direction.
* It has a strong computer-vision ecosystem.
* It works well with FastAPI.
* It can later integrate OpenCV and face-analysis modules.
* It is useful for machine learning and data science.
* It is suitable for building a structured backend.

The backend will initially focus on normal application functionality.

Advanced AI processing will not be required for the first working version.

---

### 5.2 FastAPI

FastAPI will be used to build the backend REST API.

It will handle:

* User registration
* Login and logout
* Authentication
* Role-based authorization
* User profile management
* Test creation
* MCQ question creation
* Test-code generation
* Test-code validation
* Test details
* Examination attempts
* Answer submission
* Result calculation
* Examination history
* Proctoring event storage
* Teacher attempt review
* Admin management

FastAPI is selected because it provides:

* Clear API route structure
* Automatic API documentation
* Request and response validation
* Good performance
* Strong Python integration
* Easy React integration
* Support for asynchronous operations where needed

---

### 5.3 Uvicorn

Uvicorn will be used as the development and application server for FastAPI.

It will run the backend locally and support deployment in a production environment.

Example development command:

```bash
uvicorn app.main:app --reload
```

The exact command may change according to the final backend folder structure.

---

### 5.4 Pydantic

Pydantic will be used for validating incoming and outgoing API data.

It will validate:

* Registration data
* Login data
* User profile information
* Test details
* MCQ question data
* Answer options
* Answer submissions
* Test-code requests
* Proctoring event data
* API responses

Pydantic will help prevent invalid or incomplete data from entering the backend.

---

## 6. Database Stack

### 6.1 PostgreSQL

PostgreSQL will be used as the primary relational database.

It will store:

* Users
* Roles
* Tests
* Questions
* Answer options
* Test codes
* Examination attempts
* Submitted answers
* Results
* Proctoring events
* Basic account status information

The first version does not require separate tables for complex scheduling, candidate assignment, payments, or subscriptions.

PostgreSQL is selected because it is:

* Open source
* Reliable
* Suitable for relational data
* Suitable for connected entities
* Well supported by deployment platforms
* Compatible with SQLModel and Alembic
* Appropriate for a college major project

---

### 6.2 SQLModel

SQLModel will be used for defining database models and interacting with PostgreSQL.

SQLModel combines concepts from:

* Pydantic
* SQLAlchemy

It will be used for:

* Table definitions
* Relationships
* Database queries
* Creating records
* Updating records
* Deleting records
* Retrieving records
* Basic database constraints

Possible models include:

```text
User
Test
Question
Option
Attempt
Answer
Result
ProctoringEvent
```

The exact model names and relationships will be finalized during implementation.

---

### 6.3 Alembic

Alembic will be used for database migrations.

Migrations will track changes such as:

* Creating new tables
* Adding new columns
* Updating relationships
* Adding constraints
* Modifying database structure
* Updating indexes

Database changes should be managed through migrations rather than manually changing the production database.

---

## 7. Authentication and Security

### 7.1 Authentication Method

Proxam AI will use JWT-based authentication stored in secure HTTP-only cookies.

The authentication flow will be:

```text
User submits login form
        ↓
Backend verifies credentials
        ↓
Backend creates authentication token
        ↓
Token is stored in an HTTP-only cookie
        ↓
Browser sends the cookie with protected requests
        ↓
Backend verifies the token
        ↓
User receives authorized access
```

HTTP-only cookies are selected because JavaScript cannot directly read them, reducing exposure to certain client-side token theft risks.

The cookie configuration should consider:

* `HttpOnly`
* `Secure` in production
* Appropriate `SameSite` policy
* Limited expiration time
* Correct cookie domain and path

Because authentication uses cookies, the application should also consider CSRF protection for state-changing requests.

---

### 7.2 User Roles

The initial system will support:

* Student
* Teacher
* Admin

Role-based access control will determine which routes and actions each user can access.

Examples:

* A student cannot create a test.
* A teacher cannot access another teacher’s private test-management actions.
* A teacher can view attempts for tests they created.
* An admin can access administrative management screens.
* A student can view only their own attempts and results.

---

### 7.3 Password Hashing

Passwords will never be stored as plain text.

The backend will use:

```text
pwdlib + Argon2
```

for password hashing and verification.

The database will store only password hashes.

---

### 7.4 Initial Security Requirements

The first version should include:

* Password hashing
* Protected API routes
* Role-based authorization
* Input validation
* Secure HTTP-only cookies
* Environment variables for secrets
* CORS configuration
* Basic rate limiting where necessary
* Server-side test authorization
* Server-side attempt authorization
* Server-side answer validation
* Server-side result calculation
* Protection against duplicate submissions
* Basic request error handling
* Safe handling of expired examination attempts

The frontend must never be trusted as the only source of authorization or result calculation.

---

## 8. AI-Assisted Proctoring Stack

### 8.1 Browser-Based Monitoring

The first version will run basic AI-assisted monitoring inside the student’s browser.

The browser will handle:

* Webcam access
* Face presence detection
* Multiple-face detection
* Basic looking-away estimation
* Microphone status
* Fullscreen status
* Tab-switch detection
* Network connection status

This approach avoids continuously uploading or recording examination video.

---

### 8.2 MediaPipe

MediaPipe will be used for browser-based face and facial landmark detection.

It may support:

* Face presence detection
* Multiple-face detection
* Facial landmark tracking
* Basic head-pose estimation
* Basic looking-away estimation

MediaPipe will run on the frontend where practical.

The system will not treat AI detection as a final declaration of cheating.

Instead, it will record events for later review.

The exact MediaPipe package or model will be finalized during implementation according to browser compatibility and available documentation.

---

### 8.3 Webcam and Microphone Access

The browser’s MediaDevices API will be used to request webcam and microphone access.

The application will:

* Ask for permission before the examination
* Display webcam status
* Display microphone status
* Detect permission denial
* Detect unavailable devices
* Detect camera disconnection
* Detect microphone access problems
* Display troubleshooting instructions
* Prevent examination start if required checks are not satisfied

Example API:

```javascript
navigator.mediaDevices.getUserMedia({
  video: true,
  audio: true
});
```

No continuous video or audio recording will be implemented in the initial version.

---

### 8.4 Fullscreen Monitoring

The Fullscreen API will be used to request and monitor fullscreen mode.

The system may record events such as:

* Fullscreen entered
* Fullscreen exited
* Fullscreen permission denied
* Fullscreen request failed

Fullscreen should be requested when the active examination begins.

The application must handle browser restrictions and should not assume that fullscreen activation is always successful.

---

### 8.5 Tab-Switch Monitoring

The Page Visibility API will be used to detect when the examination page becomes hidden.

The system may record events such as:

* Tab switched
* Browser minimized
* Examination window hidden
* Page visibility restored

The system should distinguish between:

* An event being detected
* A possible policy violation
* A final conclusion about student behavior

A tab-switch event must not automatically be labelled as cheating.

---

### 8.6 Proctoring Event Types

Possible event types include:

```text
camera_disconnected
microphone_unavailable
face_not_detected
multiple_faces_detected
looking_away
fullscreen_exited
tab_visibility_changed
network_interrupted
identity_check_failed
```

These events should be stored as metadata.

An event may include:

* Event ID
* Attempt ID
* Event type
* Timestamp
* Severity
* Duration where applicable
* Additional technical details

---

### 8.7 Proctoring Event Flow

```text
Browser monitoring detects an event
        ↓
Frontend classifies the event
        ↓
Frontend sends event metadata to backend
        ↓
Backend validates the event
        ↓
Backend stores the event in PostgreSQL
        ↓
Teacher or admin reviews the event later
```

Example event:

```json
{
  "event_type": "multiple_faces_detected",
  "timestamp": "2026-09-17T10:30:00Z",
  "severity": "warning"
}
```

The backend should validate:

* Whether the attempt exists
* Whether the attempt belongs to the authenticated student
* Whether the attempt is currently active
* Whether the event type is supported
* Whether the timestamp and data are valid

---

## 9. Advanced AI Features Later

Advanced AI features will not be implemented in the first stage unless they become necessary.

Possible future technologies include:

* Python
* OpenCV
* Face-analysis libraries
* Face embeddings
* Advanced identity verification
* Liveness detection
* Anti-spoofing models
* Dedicated AI-processing services

These features may be implemented as a separate Python module or service if the project becomes more complex.

The initial architecture should not depend on these advanced features.

---

## 10. API Communication

The frontend and backend will communicate through REST APIs.

Example communication flow:

```text
React frontend
      ↓
HTTP request
      ↓
FastAPI endpoint
      ↓
Request validation
      ↓
Authentication and authorization
      ↓
Business logic
      ↓
Database operation
      ↓
JSON response
      ↓
React updates the interface
```

### Example API Categories

```text
/auth
/users
/tests
/attempts
/answers
/results
/proctoring
/admin
```

The final route names may be adjusted during backend implementation.

### Example Operations

```text
POST   /auth/register
POST   /auth/login
POST   /auth/logout
GET    /auth/me

GET    /tests
POST   /tests
GET    /tests/{test_id}
POST   /tests/validate-code

POST   /attempts
GET    /attempts/{attempt_id}
POST   /attempts/{attempt_id}/answers
POST   /attempts/{attempt_id}/submit

GET    /results/{attempt_id}

POST   /proctoring/events
GET    /tests/{test_id}/attempts
```

These are example structures, not final mandatory routes.

---

## 11. Testing Stack

### 11.1 Pytest

Pytest will be used for backend testing.

It will test:

* User registration
* Login and logout
* Authentication
* Role-based authorization
* Test creation
* MCQ question creation
* Test-code generation
* Test-code validation
* Examination attempt creation
* Answer submission
* Result calculation
* Duplicate submission prevention
* Proctoring event storage
* Validation errors
* Unauthorized access

---

### 11.2 HTTPX

HTTPX will be used to test FastAPI endpoints.

It will help verify:

* API status codes
* Request validation
* Response data
* Authentication behavior
* Protected routes
* Role restrictions
* Error handling
* Database-related API behavior

---

### 11.3 Frontend Testing

Frontend testing may be introduced using a JavaScript testing tool such as Vitest.

The first priority will be:

1. Backend API testing
2. Authentication testing
3. Role-based access testing
4. Test creation testing
5. Examination workflow testing
6. Answer submission testing
7. Result calculation testing
8. Proctoring event testing
9. Critical frontend interaction testing

---

## 12. Deployment Stack

### 12.1 Frontend

The React frontend will be deployed using Vercel.

Vercel will host:

* Landing page
* Authentication screens
* Student dashboard
* Teacher dashboard
* Admin dashboard
* Test creation screens
* Examination interface
* Result pages
* Profile pages

The frontend deployment will require:

* Production build configuration
* Backend API URL
* Environment variables
* SPA route fallback configuration where necessary

---

### 12.2 Backend

The FastAPI backend may be deployed using:

* Render
* Railway

The backend deployment will require:

* Python runtime
* Production server command
* Environment variables
* Database connection string
* CORS configuration
* Secure cookie configuration
* Migration execution
* Logging configuration

Example production command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The exact deployment command may depend on the hosting provider.

---

### 12.3 Database

The PostgreSQL database may be hosted using:

* Neon
* Supabase

The selected provider should support:

* PostgreSQL database access
* Secure connection strings
* SQLModel compatibility
* Alembic migrations
* Database backups or recovery options
* Suitable connection limits

---

## 13. Environment Configuration

Sensitive values must not be hardcoded in source code.

Environment variables may include:

```env
DATABASE_URL=
JWT_SECRET_KEY=
JWT_ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
FRONTEND_URL=
BACKEND_URL=
COOKIE_SECURE=
COOKIE_SAMESITE=
```

The exact variables will be finalized during implementation.

A `.env` file should be used locally, while deployment platforms should store environment variables through their secure configuration system.

The `.env` file must not be committed to GitHub.

A `.env.example` file should be included with placeholder values.

---

## 14. Architecture Style

Proxam AI will initially use a **modular monolith architecture**.

This means the application will have one backend application, but its code will be divided into clear modules.

### Suggested Backend Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── tests.py
│   │   ├── attempts.py
│   │   ├── results.py
│   │   ├── proctoring.py
│   │   └── admin.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── test_service.py
│   │   ├── attempt_service.py
│   │   ├── result_service.py
│   │   └── proctoring_service.py
│   └── migrations/
└── tests/
```

The exact folder structure may change, but responsibilities should remain separated.

### Why Modular Monolith?

This approach is preferred over microservices because:

* It is easier to learn.
* It is easier to develop.
* It is easier to debug.
* It requires less deployment configuration.
* It is sufficient for a college major project.
* It avoids unnecessary network communication between services.
* It can later be separated into services if required.

---

## 15. Frontend Architecture Guidelines

The frontend should also be organized into reusable modules.

### Suggested Structure

```text
frontend/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── ui/
│   │   ├── layout/
│   │   ├── forms/
│   │   └── proctoring/
│   ├── pages/
│   │   ├── public/
│   │   ├── auth/
│   │   ├── student/
│   │   ├── teacher/
│   │   └── admin/
│   ├── routes/
│   ├── services/
│   │   └── api.js
│   ├── hooks/
│   ├── context/
│   ├── utils/
│   ├── styles/
│   ├── App.jsx
│   └── main.jsx
```

The frontend should separate:

* Reusable UI components
* Page-level components
* API communication
* Authentication state
* Proctoring logic
* Form validation
* Utility functions

---

## 16. Technologies Not Included Initially

The following technologies will not be used in the first version unless a clear requirement appears:

* Node.js backend
* Express
* Django
* Microservices
* Docker
* Kubernetes
* WebSockets
* Redis
* Kafka
* GraphQL
* Continuous video recording
* Continuous audio recording
* Advanced liveness detection
* Complex face-recognition pipelines
* Cloud AI APIs
* Google or social login
* Payment gateway
* Subscription system
* Native mobile application
* Complex scheduling system
* Candidate assignment system
* Public examination marketplace
* Separate question bank
* Multiple question types
* Descriptive questions
* Coding questions
* Advanced enterprise analytics

Avoiding these technologies and features will keep the first implementation manageable.

---

## 17. Initial Implementation Priority

The project will be implemented in the following order:

### Phase 1 — Project Setup

1. Create React + Vite frontend
2. Configure Tailwind CSS
3. Create the design-token system
4. Create the basic page layout
5. Create FastAPI backend
6. Configure PostgreSQL connection
7. Configure environment variables
8. Configure Git and GitHub

### Phase 2 — Authentication

9. Create user model
10. Create registration API
11. Create login API
12. Create logout API
13. Implement JWT authentication
14. Configure HTTP-only cookies
15. Implement password hashing
16. Implement protected routes
17. Implement role-based access

### Phase 3 — Teacher Test Creation

18. Create test model
19. Create question and option models
20. Create test-details form
21. Create MCQ question form
22. Implement test preview
23. Generate unique test code
24. Save the test in PostgreSQL
25. Display test-creation success screen

### Phase 4 — Student Examination Workflow

26. Create Enter Test Code screen
27. Validate test code
28. Display test details
29. Create examination attempt
30. Implement pre-exam instructions
31. Implement system-check screen
32. Implement active examination interface
33. Implement question navigation
34. Save selected answers
35. Implement timer
36. Implement submission confirmation
37. Submit examination

### Phase 5 — Results and Records

38. Validate submitted answers on the backend
39. Calculate results on the backend
40. Store result information
41. Display student result
42. Display student examination history
43. Display teacher attempts
44. Display teacher results

### Phase 6 — Basic Proctoring

45. Request webcam permission
46. Request microphone permission
47. Display camera and microphone status
48. Implement fullscreen monitoring
49. Implement tab-switch monitoring
50. Implement network-status monitoring
51. Integrate MediaPipe face presence detection
52. Implement multiple-face detection
53. Implement basic looking-away estimation
54. Store proctoring event metadata
55. Display proctoring events to authorized reviewers

### Phase 7 — Admin and Testing

56. Create admin dashboard
57. Create user management
58. Create test management
59. Create proctoring alert review
60. Test authentication
61. Test role permissions
62. Test test-code validation
63. Test examination submission
64. Test result calculation
65. Test proctoring events

### Phase 8 — Deployment

66. Deploy PostgreSQL database
67. Run database migrations
68. Deploy FastAPI backend
69. Configure production environment variables
70. Deploy React frontend
71. Configure frontend-backend communication
72. Test the deployed application

The normal examination workflow should be working before advanced proctoring features are added.

---

## 18. Final Stack Decision

The initial Proxam AI stack is:

```text
Frontend:
React
Vite
JavaScript
Tailwind CSS
CSS Variables
React Router

Backend:
Python
FastAPI
Uvicorn
Pydantic

Database:
PostgreSQL
SQLModel
Alembic

Authentication:
JWT
HTTP-only Cookies
pwdlib
Argon2

Browser Proctoring:
MediaPipe
MediaDevices API
Fullscreen API
Page Visibility API
Browser JavaScript APIs

Testing:
Pytest
HTTPX
Vitest later

Deployment:
Vercel
Render or Railway
Neon or Supabase

Version Control:
Git
GitHub
```

The project will prioritize:

* Simplicity
* Maintainability
* Security
* Clear architecture
* Gradual learning
* Reliable examination workflow
* Transparent AI-assisted monitoring

The project will not depend on advanced AI, microservices, or complex infrastructure for its first working version.
