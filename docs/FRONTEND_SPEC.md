# Proxam AI — Frontend Specification

## 1. Document Purpose

This document defines the frontend structure, screens, navigation, components, user interactions, and interface requirements for Proxam AI.

Proxam AI is a browser-based online examination platform with AI-assisted proctoring. It allows teachers to create MCQ-based tests, generate unique test codes, and share those codes with students. Students can enter a valid test code, complete the examination, and view their results.

The frontend will provide separate experiences for:

* Students
* Teachers
* Administrators

This specification focuses on:

* Required screens
* User journeys
* Navigation
* Dashboard structure
* Test creation
* Test-code entry
* Examination experience
* Result display
* Profile pages
* Basic AI-proctoring interface
* Admin management
* Forms and validation
* Accessibility
* Responsive behavior
* Frontend security expectations

Visual styling, colors, typography, spacing, and design tokens will be defined separately in `DESIGN.md`.

---

## 2. Product Scope

The first version of Proxam AI will support:

* Teacher-created examinations
* MCQ-based questions
* Unique test-code generation
* Student test-code entry
* Timed examinations
* Automatic and manual submission
* Basic AI-assisted proctoring
* Result calculation
* Teacher examination records
* Student examination records
* Basic administrator management

The first version will not attempt to become a complete enterprise examination-management platform.

The interface should remain simple, clear, and easy to understand.

---

## 3. Confirmed Application Flow

```text
Landing Page
    ↓
Login Page
    ├── Registration
    ├── Forgot Password
    └── Successful Login
            ├── Teacher Dashboard
            ├── Student Dashboard
            └── Admin Dashboard
```

### Teacher Flow

```text
Teacher Login
    ↓
Teacher Dashboard
    ↓
Create Test
    ↓
Enter Test Details
    ↓
Add MCQ Questions
    ↓
Preview Test
    ↓
Create Test
    ↓
Unique Test Code Generated
    ↓
Test Created Successfully
    ↓
Teacher Dashboard / Test Records
```

### Student Flow

```text
Student Login
    ↓
Student Dashboard
    ↓
Enter Test Code
    ↓
Valid Test Found
    ↓
Exam Details
    ↓
Pre-Exam System Check
    ↓
Start Exam
    ↓
Complete MCQ Examination
    ↓
Submit Exam
    ↓
Result Page
    ↓
Student Dashboard / Exam Records
```

### Profile Flow

```text
Teacher or Student Dashboard
    ↓
Click Profile Avatar
    ↓
Profile Page
```

### Admin Flow

```text
Admin Login
    ↓
Admin Dashboard
    ├── User Management
    ├── Test Management
    ├── Proctoring Alerts
    ├── Basic Reports
    └── Admin Profile
```

---

## 4. User Roles

Proxam AI will support three primary roles.

### 4.1 Student

Students can:

* Log in
* Register
* View their dashboard
* Enter a test code
* View test details
* Complete pre-exam checks
* Attempt an examination
* Submit an examination
* View published results
* View their own examination records
* View and edit their profile
* Change their password
* Log out

Students cannot:

* Create tests
* Edit tests
* View other students’ results
* View teacher records
* Access admin features
* View private proctoring information belonging to other students

### 4.2 Teacher

Teachers can:

* Log in
* Register
* View their dashboard
* Create MCQ tests
* Add and edit questions while creating a test
* Preview a test
* Generate a unique test code
* View their created-test records
* View test details
* View student attempts and results for their own tests
* View permitted proctoring alerts
* View and edit their profile
* Change their password
* Log out

Teachers cannot:

* Access platform-wide administration
* Manage unrelated teachers’ tests
* Access unrelated students’ private information
* Modify system-wide settings

### 4.3 Administrator

Administrators can:

* View the admin dashboard
* View and manage users
* View and manage tests
* View basic platform activity
* View authorized proctoring alerts
* View basic platform reports
* Manage their own profile
* Access selected system settings if implemented

Sensitive administrator actions should be recorded in audit logs.

---

## 5. Application Areas

The frontend will contain the following major areas.

```text
Proxam AI
│
├── Public Area
│   └── Landing Page
│
├── Authentication Area
│   ├── Login
│   ├── Registration
│   ├── Forgot Password
│   └── Reset Password
│
├── Teacher Area
│   ├── Teacher Dashboard
│   ├── Create Test
│   ├── Test Preview
│   ├── Test Created Successfully
│   ├── Test Details
│   └── Teacher Profile
│
├── Student Area
│   ├── Student Dashboard
│   ├── Enter Test Code
│   ├── Exam Details
│   ├── Pre-Exam System Check
│   ├── Active Examination
│   ├── Submission Confirmation
│   ├── Exam Submitted
│   ├── Result Page
│   └── Student Profile
│
└── Admin Area
    ├── Admin Dashboard
    ├── User Management
    ├── User Details
    ├── Test Management
    ├── Test Details
    ├── Proctoring Alerts
    ├── Basic Reports
    └── Admin Profile
```

---

## 6. Global Layout

### 6.1 Public Layout

The public layout may contain:

* Proxam AI logo
* Landing-page navigation
* Login button
* Registration button
* Main content
* Footer

The landing page has already been designed and should not be unnecessarily redesigned.

### 6.2 Authentication Layout

Authentication pages should use a focused layout containing:

* Proxam AI branding
* Form title
* Form fields
* Primary action
* Supporting links
* Validation messages

Authentication pages should not contain dashboard navigation.

### 6.3 Dashboard Layout

The dashboard layout should follow the already-designed dashboard structure.

It may contain:

* Top header
* Proxam AI logo
* Current page title
* User avatar/profile menu
* Main content area
* Role-specific dashboard content
* Logout action

A permanent sidebar is not mandatory.

The final navigation should follow the existing visual design rather than forcing a new sidebar-based structure.

### 6.4 Examination Layout

The active examination should use a separate distraction-minimized layout.

It should:

* Hide normal dashboard navigation
* Display the test title
* Display the remaining time
* Display the current question
* Display MCQ options
* Display question navigation
* Display submission controls
* Display monitoring status
* Display necessary warnings

---

## 7. Public and Authentication Screens

### 7.1 Landing Page

The landing page has already been designed.

It should introduce:

* Proxam AI
* Online examination functionality
* Teacher test creation
* Student test participation
* AI-assisted proctoring
* Basic privacy and transparency information
* Login and registration actions

The landing page should not claim that cheating is impossible or that AI decisions are always correct.

### 7.2 Login Page

The login page has already been designed.

Fields:

* Email or username
* Password

Actions:

* Login
* Forgot password
* Register
* Show or hide password

Requirements:

* Validate required fields
* Display incorrect-credentials message
* Display loading state
* Prevent repeated accidental submissions
* Redirect the user according to their role

### 7.3 Registration Page

The registration page has already been designed.

Possible fields:

* Full name
* Email
* Password
* Confirm password
* Role selection, if required
* Basic academic or professional information, if required

Requirements:

* Validate required fields
* Validate email format
* Validate password requirements
* Confirm password match
* Prevent duplicate registration
* Display registration success or failure

The registration process should not collect unnecessary information.

### 7.4 Forgot Password Page

The forgot-password page has already been designed.

Fields:

* Registered email

Requirements:

* Display confirmation after submission
* Avoid revealing whether an email exists
* Provide clear next steps
* Display loading and error states

### 7.5 Reset Password Page

This page may be implemented after the forgot-password flow.

Fields:

* New password
* Confirm password

Requirements:

* Validate password requirements
* Confirm password match
* Handle expired or invalid reset links
* Display success after password reset

---

## 8. Teacher Frontend

## 8.1 Teacher Dashboard

The teacher dashboard has already been designed.

It should contain:

* Teacher brief information
* Teacher name
* Profile/avatar
* Create Test button
* Teacher’s test records

Each test record may display:

* Test title
* Unique test code
* Number of questions
* Duration
* Creation date
* Number of attempts
* Test status
* View details action

The dashboard should prioritize the Create Test action and the teacher’s existing records.

The first version does not need excessive statistics or complex charts.

### Possible Test Statuses

* Draft
* Created
* Active
* Completed
* Closed

Only statuses required by the actual implementation should be displayed.

---

## 8.2 Create Test Page

The Create Test page opens when the teacher clicks the Create Test button.

The page should allow the teacher to enter:

* Test title
* Subject or category, if required
* Test description
* Test instructions
* Duration
* Total marks
* Number of questions
* Passing marks, if required
* Questions
* Four answer options for each question
* Correct answer for each question

The first version will support MCQ questions only.

### Main Actions

* Add question
* Edit question
* Remove question
* Preview test
* Create test
* Cancel

### Required Validation

* Test title cannot be empty
* Duration must be valid
* At least one question must be added
* Question text cannot be empty
* All required options must be filled
* One correct answer must be selected
* Marks must be valid
* Duplicate or empty options should be handled appropriately

---

## 8.3 Add MCQ Question

The question form should contain:

* Question text
* Option A
* Option B
* Option C
* Option D
* Correct answer
* Marks, if configured
* Explanation, if results support explanations

The teacher should be able to:

* Add a question
* Edit a question
* Delete a question
* Select the correct answer
* Reorder questions, if implemented

The first version should not include coding questions, subjective answers, or complex question types.

---

## 8.4 Test Preview Page

The preview page allows the teacher to see how the test will appear to students.

It should display:

* Test title
* Instructions
* Duration
* Questions
* Answer options
* Question numbering
* Total marks

The preview should not allow the teacher to submit an actual attempt.

Actions:

* Back to editing
* Create test

---

## 8.5 Test Created Successfully Page

After successful test creation, the system should display:

* Success message
* Test title
* Unique test code
* Copy code button
* Share code button, if implemented
* Number of questions
* Test duration
* Test status
* Go to dashboard button
* View test details button

Example:

```text
Test Created Successfully

Your test is ready.

Test Code:
PXAM-7K4Q2

[Copy Code] [View Test]
[Go to Dashboard]
```

The unique code must be generated by the backend and must be unique for the test.

The frontend must not generate or trust the code by itself.

---

## 8.6 Test Details Page

The test details page may open when the teacher selects a test record.

It should display:

* Test title
* Test code
* Description
* Instructions
* Number of questions
* Duration
* Total marks
* Creation date
* Test status
* Number of attempts
* Result information, if available

Possible actions:

* Copy test code
* View attempts
* View results
* Close test, if implemented

The teacher should only be able to access tests created by that teacher.

---

## 8.7 Teacher Records

Teacher records should be available directly on the teacher dashboard or through a dedicated records view.

Records may include:

* Test title
* Test code
* Creation date
* Number of questions
* Duration
* Student attempt count
* Completion count
* Test status
* View details action

A separate advanced examination-management page is not required for the first version.

---

## 8.8 Teacher Profile Page

The teacher profile page opens when the teacher clicks the avatar or profile picture.

It may contain:

* Profile image
* Full name
* Email
* Role
* Institution or department, if required
* Edit profile action
* Change password action
* Logout action

The profile page should not contain test-management features.

---

## 9. Student Frontend

## 9.1 Student Dashboard

The student dashboard has already been designed.

It should contain:

* Student brief information
* Student name
* Profile/avatar
* Enter Code button
* Student examination records

Each student record may display:

* Test title
* Test date
* Attempt status
* Score, if published
* Result status
* View result action

The dashboard should prioritize the Enter Code action.

The student should not need to browse a large examination marketplace or examination catalogue.

---

## 9.2 Enter Test Code

When the student clicks Enter Code, display a code-entry interface.

This may be:

* A modal on the student dashboard, or
* A separate centered page

The interface should contain:

* Test code input
* Continue button
* Cancel button, if modal-based

Possible validation messages:

* Test code is required
* Test code is invalid
* Test does not exist
* Test is closed
* Test is expired
* Student has already attempted this test
* Test is not currently available

The backend must validate the code. The frontend must not assume that a code is valid only because it follows a particular format.

---

## 9.3 Exam Details Page

After a valid test code is entered, display the exam details.

The page should contain:

* Test title
* Teacher name, if permitted
* Description
* Instructions
* Number of questions
* Duration
* Total marks
* Passing criteria, if configured
* Proctoring requirements
* Start Exam button

The student should be able to review the information before starting.

The system should not start the examination immediately after code validation.

---

## 9.4 Pre-Exam System Check Page

Before starting the examination, the system should check the required device and browser conditions.

Checks may include:

* Browser compatibility
* Camera permission
* Camera availability
* Microphone permission
* Microphone availability
* Internet connection
* Fullscreen capability
* Face visibility
* Identity verification, if implemented

Each check should display a clear status:

* Checking
* Passed
* Failed
* Permission Required
* Not Available

The page should provide:

* Retry action
* Permission instructions
* Troubleshooting guidance
* Continue button after required checks pass

The exact identity-verification method will be finalized during technical implementation.

---

## 9.5 Active Examination Page

The active examination page is the main student examination interface.

### Required Elements

* Test title
* Remaining time
* Current question number
* Total question count
* Question text
* Four MCQ options
* Question palette
* Previous button
* Next button
* Clear answer button
* Mark for review button, if implemented
* Submit button
* Monitoring status
* Connection status

### Question States

* Not Visited
* Visited
* Answered
* Not Answered
* Marked for Review
* Answered and Marked for Review

The selected answer should remain saved when the student moves between questions.

The system should save answers safely whenever possible.

---

## 9.6 Examination Timer

The timer should:

* Display remaining time clearly
* Update continuously
* Warn the student when time is low
* Prevent negative time display
* Trigger automatic submission when time expires

The timer should be based on server-controlled examination timing rather than relying only on the browser’s local clock.

---

## 9.7 Question Navigation

Students should be able to:

* Move to the next question
* Move to the previous question
* Select a question from the question palette
* Clear a selected answer
* Mark a question for review, if implemented
* Return to marked questions

Question navigation should not erase previously selected answers.

---

## 9.8 Webcam and Monitoring Interface

During the examination, the frontend may display a small floating webcam preview.

The preview should contain:

* Live camera feed
* Monitoring status
* Camera status indicator
* Face-detection status, if available

The webcam preview should remain small enough that it does not distract from the question area.

Example:

```text
┌───────────────────────┐
│                       │
│    Webcam Preview     │
│                       │
│ ● Monitoring Active   │
└───────────────────────┘
```

The exact placement will be finalized in `DESIGN.md`.

The frontend should not display a large surveillance-style interface to the student.

---

## 9.9 Proctoring Warnings

Proctoring warnings should preferably appear as:

* Toast notifications
* Small warning banners
* Modals for serious or blocking issues

Possible warning situations:

* Camera permission removed
* Camera disconnected
* Microphone disconnected
* Face not detected
* Multiple faces detected
* Fullscreen exited
* Examination tab became inactive
* Network connection unstable
* Proctoring temporarily unavailable

Warnings should be:

* Clear
* Specific
* Non-accusatory
* Actionable

Example:

```text
Your face is not visible.

Please adjust your position so that your face
remains visible in the camera.

[Acknowledge]
```

The system should not automatically label a student as dishonest based only on a detection event.

---

## 9.10 Submission Confirmation

Before manual submission, display:

* Answered question count
* Unanswered question count
* Marked-for-review count, if implemented
* Remaining time
* Confirmation message

Actions:

* Return to examination
* Confirm submission

Automatic submission should display a separate explanation that the test ended because the time expired.

---

## 9.11 Exam Submitted Page

After successful submission, display:

* Success message
* Test title
* Submission time
* Result status
* View result button, if results are available
* Back to dashboard button

Example:

```text
Test Submitted Successfully

Your answers have been submitted.

[View Result]
[Back to Dashboard]
```

The interface should not claim successful submission until the backend confirms it.

---

## 9.12 Result Page

The result page may display:

* Student name
* Test title
* Submission date
* Total questions
* Correct answers
* Incorrect answers
* Unanswered questions
* Score
* Maximum marks
* Percentage
* Passing status, if configured
* Result publication status

If the teacher has not published the result, display:

```text
Your result is not published yet.
```

The student should only see their own result.

Detailed answer review may be implemented later and is not required for the first version.

---

## 9.13 Student Examination Records

The student dashboard should display previous examination records.

Each record may contain:

* Test title
* Attempt date
* Attempt status
* Score, if published
* Result status
* View result action

Possible statuses:

* Not Started
* In Progress
* Submitted
* Auto-Submitted
* Result Pending
* Result Published

The student should only see their own records.

---

## 9.14 Student Profile Page

The student profile page opens when the student clicks the avatar or profile picture.

It may contain:

* Profile image
* Full name
* Email
* Student ID, if required
* Course or department, if required
* Edit profile action
* Change password action
* Logout action

---

## 10. Admin Frontend

The admin panel should remain simple and focused on platform management.

## 10.1 Admin Dashboard

The admin dashboard may display:

* Total students
* Total teachers
* Total tests
* Total attempts
* Active tests
* Completed tests
* Recent platform activity
* Recent proctoring alerts

The dashboard should use simple statistics and tables rather than excessive charts.

---

## 10.2 User Management Page

The user-management page should display:

* User name
* Email
* Role
* Account status
* Registration date
* Actions

Filters may include:

* All users
* Students
* Teachers
* Administrators

Possible actions:

* View user
* Activate account
* Deactivate account
* View activity, if implemented

The first version does not need complex role-permission editing.

---

## 10.3 User Details Page

The user details page may display:

* Name
* Email
* Role
* Account status
* Registration date
* Created tests, for teachers
* Attempted tests, for students
* Account actions

The admin should not see unnecessary private information.

---

## 10.4 Test Management Page

The test-management page should display all tests created on the platform.

Each record may contain:

* Test title
* Teacher name
* Test code
* Number of questions
* Number of attempts
* Test status
* Creation date

Possible actions:

* View test details
* View attempts
* Close test, if implemented
* Delete test, if authorized

---

## 10.5 Test Details Page

The test details page may display:

* Test title
* Test code
* Teacher information
* Number of questions
* Duration
* Creation date
* Number of attempts
* Result summary
* Test status

The admin should have read access to platform tests and only authorized management actions.

---

## 10.6 Proctoring Alerts Page

The proctoring-alerts page should display basic monitoring events.

Each alert may contain:

* Student name
* Test title
* Alert type
* Date and time
* Status
* Review action

Possible alert types:

* Face not detected
* Multiple faces detected
* Tab switched
* Fullscreen exited
* Camera disconnected
* Microphone disconnected

The first version does not need a complex investigation dashboard.

---

## 10.7 Proctoring Alert Details

The alert-details view may display:

* Student information
* Test information
* Attempt information
* Alert type
* Timestamp
* Event description
* Review status
* Reviewer notes, if implemented

Detected events should be treated as indicators requiring human review rather than automatic proof of misconduct.

---

## 10.8 Basic Reports Page

The reports page may display:

* Total tests
* Total attempts
* Completed attempts
* Average score
* Test participation
* Result publication status
* Proctoring alert count

Advanced enterprise analytics are not required for the first version.

---

## 10.9 Admin Profile Page

The admin profile page may contain:

* Profile image
* Admin name
* Email
* Role
* Edit profile action
* Change password action
* Logout action

---

## 11. Shared Components

### Navigation Components

* Header
* Logo
* User avatar
* Profile menu
* Role-based navigation
* Mobile navigation, where required

A permanent sidebar is optional and should only be used if it matches the approved dashboard design.

### Form Components

* Text input
* Password input
* Textarea
* Select
* Checkbox
* Radio button
* Date input, if required
* Time input, if required
* Form error message

### Feedback Components

* Alert
* Toast
* Confirmation dialog
* Warning banner
* Success message
* Error message
* Loading indicator
* Progress indicator

### Data Components

* Test record
* Result record
* User table
* Search input, if required
* Filter control, if required
* Status badge
* Empty-state panel

### Examination Components

* Question card
* Answer option
* Question palette
* Timer
* Exam progress indicator
* Monitoring status indicator
* Webcam preview
* Submission dialog

### Profile Components

* Profile header
* Profile information
* Edit profile form
* Change-password form
* Logout action

---

## 12. Forms and Validation

All forms should provide:

* Clear labels
* Required-field indicators
* Helpful validation messages
* Field-level error messages
* Loading state during submission
* Prevention of accidental duplicate submission
* Clear success or failure feedback

Validation should occur on both frontend and backend.

The frontend must not be treated as the only security layer.

---

## 13. States and Error Handling

Important screens should define the following states.

### General States

* Loading
* Empty
* Error
* Permission denied
* Not found
* Session expired
* Success
* Confirmation
* Network error

### Teacher States

* No tests created
* Test creation in progress
* Test creation failed
* Invalid question data
* Test code generation failed
* Test created successfully
* Test not found
* Test closed

### Student States

* No examination records
* Empty test-code field
* Invalid test code
* Test not found
* Test expired
* Test closed
* Already attempted
* Pre-exam check failed
* Camera permission denied
* Microphone permission denied
* Face not detected
* Multiple faces detected
* Fullscreen exited
* Network disconnected
* Submission in progress
* Submission successful
* Submission failed
* Result pending
* Result not published

### Admin States

* No users
* No tests
* No alerts
* No reports
* User not found
* Test not found
* Permission denied
* Data loading failed

---

## 14. Responsive Requirements

The frontend should support:

* Desktop screens
* Laptop screens
* Tablets where practical
* Mobile screens for public pages and general dashboards

The active examination should primarily target desktop and laptop screens because:

* Webcam usage is more practical
* Question navigation requires sufficient space
* Fullscreen monitoring is more reliable
* Small screens may reduce examination usability

If mobile examination is not supported, the pre-exam screen should clearly communicate the supported device requirements.

---

## 15. Accessibility Requirements

The frontend should follow accessible development practices.

Requirements include:

* Semantic HTML
* Proper heading hierarchy
* Accessible form labels
* Keyboard navigation
* Visible focus states
* Sufficient text contrast
* Descriptive button labels
* Accessible error messages
* Screen-reader-friendly status updates
* Avoidance of color-only status indicators
* Proper alternative text for meaningful images
* Logical tab order
* Reduced-motion consideration

The examination interface should allow keyboard users to navigate questions and answer options wherever technically possible.

---

## 16. Frontend Security Requirements

The frontend should:

* Protect role-based routes
* Avoid exposing sensitive data unnecessarily
* Never store passwords
* Avoid insecure token storage
* Handle session expiration
* Prevent unauthorized navigation
* Validate user input
* Avoid displaying internal error details
* Restrict access to test, result, and proctoring information
* Display consent and permission information clearly
* Avoid trusting frontend-only role information

Actual authorization and security enforcement must be implemented on the backend.

The unique test code must be generated and validated by the backend.

---

## 17. Out-of-Scope Features

The first version will not include:

* Native mobile applications
* Dedicated desktop lockdown software
* Live video calls with proctors
* Continuous video recording
* Audio recording or transcription
* Emotion or mental-state analysis
* Subjective-answer evaluation
* Coding-question editor
* Coding-question evaluator
* Advanced biometric management
* Public examination marketplace
* Payment and subscription system
* External LMS integration
* Advanced enterprise analytics
* Complex role-permission editor
* Large reusable question-bank system
* Advanced candidate invitation system
* Complex live monitoring wall
* Automatic cheating verdicts
* Advanced liveness detection
* AI-generated questions, unless added later

---

## 18. Frontend Completion Criteria

The frontend will be considered complete when:

* The landing page is accessible
* Users can log in
* New users can register
* Users can request password recovery
* Users are redirected according to their role
* Teachers can access their dashboard
* Teachers can create MCQ tests
* Teachers can preview tests
* Each created test receives a unique code
* Teachers can view their test records
* Teachers can access their profile
* Students can access their dashboard
* Students can enter a valid test code
* Students can view exam details
* Students can complete pre-exam checks
* Students can attempt an examination
* Students can submit manually or automatically
* Students can view published results
* Students can view their examination records
* Students can access their profile
* Administrators can access the admin dashboard
* Administrators can manage basic user information
* Administrators can view platform tests
* Administrators can view basic proctoring alerts
* Examination monitoring status is visible
* Loading, empty, error, and permission states are handled
* Role-based access is enforced
* The interface is responsive on supported devices
* Accessibility requirements are considered
* Sensitive information is not exposed through unauthorized routes
