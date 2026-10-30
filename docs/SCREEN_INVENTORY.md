# Proxam AI — Screen Inventory

## 1. Document Purpose

This document lists the screens and major interface views required for the first version of Proxam AI.

It translates the project brief, frontend specification, and user flows into a practical screen inventory.

Each screen includes:

* Screen name
* Screen purpose
* Primary user role
* Main content
* Main actions
* Important states
* Access requirements

This document defines the required application screens and interface states. It does not define detailed visual styling.

Colors, typography, spacing, layout style, design tokens, and visual direction will be defined in `DESIGN.md`.

Some features may be implemented as tabs, drawers, modals, inline panels, or reusable components instead of separate routes.

---

## 2. Application Structure

The first version of Proxam AI will contain the following areas:

```text
Proxam AI
│
├── Public Screens
├── Authentication Screens
├── Student Screens
├── Teacher Screens
├── Admin Screens
└── Shared / System States
```

The main application flow is:

```text
Landing Page
    ↓
Login / Registration
    ↓
Role-Based Dashboard
    ├── Student Dashboard
    │     ├── Enter Test Code
    │     ├── Test Details
    │     ├── System Check
    │     ├── Examination
    │     ├── Submission
    │     ├── Result
    │     └── History
    │
    ├── Teacher Dashboard
    │     ├── Create Test
    │     ├── Add MCQs
    │     ├── Preview Test
    │     ├── Test Created Success
    │     ├── Test Records
    │     └── Test Details
    │
    └── Admin Panel
          ├── Admin Dashboard
          ├── User Management
          ├── Test Management
          ├── Test Details
          └── Proctoring Alerts
```

---

## 3. Screen Count

The first version will contain approximately:

| Area            | Primary Screens / Views |
| --------------- | ----------------------: |
| Public          |                       3 |
| Authentication  |                       4 |
| Student         |                       9 |
| Teacher         |                       9 |
| Admin           |                       6 |
| Shared / System |                       3 |
| **Total**       |                  **34** |

This count includes primary pages and major interface views. Some smaller actions will be implemented as modals, drawers, tabs, or contextual states.

---

# 4. Public Screens

## PUB-01 — Landing Page

**Route:** `/`

**Primary role:** Public visitor

### Purpose

Introduce Proxam AI and explain its main capabilities.

### Main content

* Platform introduction
* Short explanation of online examinations
* AI-assisted proctoring explanation
* Main features
* Examination workflow
* Privacy and human-review statement
* Login action
* Registration action

### Main actions

* Login
* Register
* Learn more
* Open help, if implemented

### Important states

* Normal
* Loading, only if dynamic content is used
* Public content error, if applicable

### Access requirements

Publicly accessible.

---

## PUB-02 — About Platform

**Route:** `/about`

**Primary role:** Public visitor

### Purpose

Explain what Proxam AI does and clarify its limitations.

### Main content

* Platform purpose
* Intended users
* Examination process
* AI-assisted monitoring explanation
* Human review policy
* Privacy and data-handling explanation
* Features included in the first version
* Features not included in the first version

### Main actions

* Login
* Register
* Return to home

### Access requirements

Publicly accessible.

---

## PUB-03 — Help / Contact

**Route:** `/help`

**Primary role:** Public visitor / authenticated user

### Purpose

Provide basic support and troubleshooting information.

### Main content

* Frequently asked questions
* Browser requirements
* Camera permission guidance
* Microphone permission guidance
* Fullscreen guidance
* Examination preparation instructions
* Basic technical support information

### Main actions

* Search help content, if implemented
* Contact support, if implemented
* Return to previous page
* Return to home

### Important states

* No search results
* Contact form validation error
* Contact submission success
* Contact submission failure

### Access requirements

Publicly accessible.

---

# 5. Authentication Screens

## AUTH-01 — Login

**Route:** `/login`

**Primary role:** All users

### Purpose

Allow registered users to access the platform.

### Main content

* Email field
* Password field
* Show/hide password control
* Login button
* Forgot-password link
* Registration link

### Main actions

* Submit login
* Open registration
* Open password recovery

### Important states

* Empty form
* Invalid credentials
* Inactive account
* Loading
* Network error
* Session already active

### Access requirements

Publicly accessible.

After successful login, the user is redirected to the dashboard associated with their role.

---

## AUTH-02 — Registration

**Route:** `/register`

**Primary role:** New user

### Purpose

Allow a new user to create an account.

### Main content

* Full name
* Email
* Password
* Confirm password
* Role selection, if users can select their role
* Basic consent information, if required

### Main actions

* Create account
* Return to login

### Important states

* Validation errors
* Email already registered
* Password mismatch
* Weak password
* Registration success
* Registration failure

### Access requirements

Publicly accessible.

---

## AUTH-03 — Forgot Password

**Route:** `/forgot-password`

**Primary role:** Registered user

### Purpose

Allow a user to request a password-reset link.

### Main content

* Email field
* Password recovery instructions

### Main actions

* Request password reset
* Return to login

### Important states

* Invalid email format
* Request submitted
* Network error

The interface should not reveal whether a particular email address exists.

### Access requirements

Publicly accessible.

---

## AUTH-04 — Reset Password

**Route:** `/reset-password`

**Primary role:** User with a valid reset link

### Purpose

Allow a user to set a new password.

### Main content

* New password
* Confirm password
* Password requirements

### Main actions

* Reset password
* Return to login

### Important states

* Invalid reset token
* Expired reset token
* Password mismatch
* Weak password
* Reset success
* Reset failure

### Access requirements

Accessible only through a valid password-reset flow.

---

# 6. Student Screens

## STUD-01 — Student Dashboard

**Route:** `/student/dashboard`

**Primary role:** Student

### Purpose

Provide the student's main overview after login.

### Main content

* Student brief information
* Enter Test Code action
* Recent examination records
* Recently completed examinations
* Recent results
* Important examination alerts
* Basic account information

### Main actions

* Enter test code
* View examination record
* View result
* Open examination history
* Open student profile

### Important states

* Loading
* No examination records
* No results
* Error loading dashboard

### Access requirements

Authenticated Student only.

---

## STUD-02 — Enter Test Code

**Route:** `/student/enter-code`

**Primary role:** Student

### Purpose

Allow a student to enter a unique test code provided by a teacher.

### Main content

* Test-code input field
* Example test-code format
* Short instructions
* Continue button

### Main actions

* Submit test code
* Clear code
* Return to dashboard

### Important states

* Empty code
* Invalid code format
* Test not found
* Test unavailable
* Test expired
* Test already attempted
* Network error
* Loading

### Access requirements

Authenticated Student only.

---

## STUD-03 — Test Details

**Route:** `/student/tests/:testId`

**Primary role:** Student

### Purpose

Display basic information about a test after a valid test code is entered.

### Main content

* Test title
* Test description
* Teacher or organization name, if available
* Number of questions
* Duration
* Total marks
* Marking information
* Examination instructions
* Proctoring requirements
* Attempt information

### Main actions

* Continue to instructions
* Start preparation
* Return to enter-code page
* Return to dashboard

### Important states

* Test not found
* Test unavailable
* Test expired
* Attempt already completed
* Attempt limit reached
* Loading
* Network error

### Access requirements

Authenticated Student with a valid test-code access request.

---

## STUD-04 — Pre-Exam Instructions and System Check

**Route:** `/student/tests/:testId/system-check`

**Primary role:** Student

### Purpose

Display examination instructions and verify that the student's device is ready.

This screen combines the instruction and system-check steps to avoid unnecessary navigation.

### Main content

* Examination rules
* Time limit
* Question and marking information
* Proctoring explanation
* Privacy notice
* Browser compatibility check
* Camera permission check
* Microphone permission check
* Camera availability
* Microphone availability
* Network status
* Fullscreen capability
* Check results
* Required acknowledgement

### Main actions

* Allow camera permission
* Allow microphone permission
* Retry checks
* Accept instructions
* Continue to verification
* Return to test details

### Important states

* Checking
* Passed
* Failed
* Permission required
* Camera unavailable
* Microphone unavailable
* Browser unsupported
* Network unstable
* Required acknowledgement missing
* Test no longer available

### Access requirements

Authenticated Student with valid access to the test.

---

## STUD-05 — Basic Identity / Face-Presence Verification

**Route:** `/student/tests/:testId/verification`

**Primary role:** Student

### Purpose

Perform a basic live camera verification step before the examination begins.

The first version will not require face matching against a registered profile photograph.

### Main content

* Verification instructions
* Camera preview
* Face-presence status
* Verification status
* Retry information
* Privacy explanation

### Main actions

* Start verification
* Retry verification
* Continue to examination
* Return to system check

### Important states

* Ready
* Processing
* Successful
* Face not detected
* Multiple faces detected
* Camera unavailable
* Verification service unavailable
* Retry limit reached

### Access requirements

Authenticated Student who has passed the system check.

---

## STUD-06 — Active Examination

**Route:** `/student/attempts/:attemptId/exam`

**Primary role:** Student

### Purpose

Provide the main timed examination interface.

### Main content

* Test title
* Remaining timer
* Current question number
* Question text
* Answer options
* Question palette
* Progress information
* Navigation controls
* Answer-saving status
* Monitoring status
* Small webcam preview or monitoring indicator
* Technical warnings

### Main actions

* Select answer
* Clear answer
* Next question
* Previous question
* Mark for review
* Open question palette
* Submit examination

### Important states

* Loading questions
* Answer saving
* Answer saved
* Answer-save failure
* Network disconnected
* Camera disconnected
* Microphone disconnected
* Face not detected
* Multiple faces detected
* Tab switched
* Fullscreen exited
* Session expired
* Examination time expired
* Automatic submission

### Access requirements

Authenticated Student with an active examination attempt.

---

## STUD-07 — Submission Confirmation

**Implementation:** Modal or in-page confirmation state

**Primary role:** Student

### Purpose

Confirm that the student wants to submit the examination.

### Main content

* Answered-question count
* Unanswered-question count
* Marked-for-review count
* Remaining time
* Submission warning

### Main actions

* Confirm submission
* Return to examination

### Important states

* Submission processing
* Submission successful
* Submission failure
* Attempt already submitted
* Time expired

### Access requirements

Available only during an active examination attempt.

---

## STUD-08 — Exam Submitted

**Route:** `/student/attempts/:attemptId/submitted`

**Primary role:** Student

### Purpose

Confirm that the examination has been submitted.

### Main content

* Submission confirmation
* Submission timestamp
* Attempt status
* Evaluation status
* Result publication information

### Main actions

* View result, if available
* Return to dashboard
* View examination history

### Important states

* Submitted successfully
* Automatically submitted
* Evaluation pending
* Result pending
* Submission status unavailable

### Access requirements

Authenticated Student who owns the submitted attempt.

---

## STUD-09 — Examination Result

**Route:** `/student/attempts/:attemptId/result`

**Primary role:** Student

### Purpose

Display the student's result after evaluation.

### Main content

* Test title
* Submission date
* Total questions
* Correct answers
* Incorrect answers
* Unanswered questions
* Score
* Percentage
* Pass/fail status, if configured
* Result publication status

### Main actions

* Return to dashboard
* Open examination history

### Important states

* Evaluation pending
* Result not published
* Result withheld
* Result under review
* Result unavailable

### Access requirements

Authenticated Student who owns the attempt and is permitted to view the result.

---

## STUD-10 — Student Records / Examination History

**Route:** `/student/history`

**Primary role:** Student

### Purpose

Display the student's previous examination attempts and results.

### Main content

* Test title
* Attempt date
* Attempt status
* Submission status
* Score, if published
* Result status
* Basic proctoring review status, if appropriate

### Main actions

* Search history
* Filter history
* View result
* Open attempt details, if implemented

### Important states

* Loading
* No examination history
* No search results
* Error loading history

### Access requirements

Authenticated Student only.

---

## STUD-11 — Student Profile

**Route:** `/student/profile`

**Primary role:** Student

### Purpose

Allow the student to view and update basic profile information.

### Main content

* Full name
* Email
* Profile photo, if implemented
* Account information
* Password-management option

### Main actions

* Edit profile
* Save changes
* Change password
* Logout

### Important states

* Loading
* Validation error
* Save success
* Save failure

### Access requirements

Authenticated Student only.

---

# 7. Teacher Screens

## TEACH-01 — Teacher Dashboard

**Route:** `/teacher/dashboard`

**Primary role:** Teacher / Examination Creator

### Purpose

Provide the teacher's main overview after login.

### Main content

* Teacher brief information
* Create Test button
* Total created tests
* Recent test records
* Active or available tests
* Recent student attempts
* Recent results
* Attempts requiring review, if implemented

### Main actions

* Create test
* View test records
* Open test details
* View attempts
* Open teacher profile

### Important states

* Loading
* No created tests
* No attempts
* No results
* Error loading dashboard

### Access requirements

Authenticated Teacher only.

---

## TEACH-02 — Teacher Test Records

**Route:** `/teacher/tests`

**Primary role:** Teacher

### Purpose

Display tests created by the teacher.

### Main content

* Test list
* Test title
* Test code
* Creation date
* Duration
* Number of questions
* Test status
* Attempt count

### Main actions

* Create test
* Search tests
* Filter tests
* Open test details
* Copy test code

### Important states

* Loading
* No tests created
* No search results
* Error loading tests

### Access requirements

Authenticated Teacher only.

---

## TEACH-03 — Create Test — Test Details

**Route:** `/teacher/tests/create`

**Primary role:** Teacher

### Purpose

Collect the basic information required to create a test.

### Main content

* Test title
* Test description
* Duration
* Total marks
* Basic marking settings
* Negative marking option, if implemented
* Basic proctoring requirement settings

### Main actions

* Continue to questions
* Cancel
* Save draft, if implemented

### Important states

* Empty form
* Validation errors
* Unsaved changes
* Save failure

### Access requirements

Authenticated Teacher only.

---

## TEACH-04 — Create Test — Add MCQ Questions

**Route:** `/teacher/tests/create/questions`

**Primary role:** Teacher

### Purpose

Allow the teacher to add single-correct MCQ questions directly to the test.

### Main content

* Question text field
* Answer option fields
* Correct-answer selection
* Marks
* Optional explanation, if implemented
* Added-question list
* Question count
* Basic question navigation

### Main actions

* Add question
* Edit question
* Delete question
* Select correct answer
* Continue to preview
* Return to test details

### Important states

* Empty question form
* Missing question text
* Missing answer option
* Missing correct answer
* Validation error
* No questions added
* Delete confirmation
* Unsaved changes

### Access requirements

Authenticated Teacher creating a test.

---

## TEACH-05 — Test Preview

**Route:** `/teacher/tests/create/preview`

**Primary role:** Teacher

### Purpose

Allow the teacher to review the test before creating it.

### Main content

* Test title
* Test description
* Duration
* Total marks
* Question list
* Answer options
* Correct-answer indication for teacher preview
* Basic proctoring settings

### Main actions

* Return to test details
* Return to question editor
* Create test

### Important states

* No questions added
* Incomplete test
* Validation error
* Loading

### Access requirements

Authenticated Teacher with a test draft.

---

## TEACH-06 — Test Creation Success

**Implementation:** Success page, modal, or dedicated result view

**Route, if required:** `/teacher/tests/:testId/created`

**Primary role:** Teacher

### Purpose

Confirm that the test was created successfully and display the generated test code.

### Main content

* Success message
* Test title
* Unique test code
* Test summary
* Basic sharing instructions

### Main actions

* Copy test code
* Share test code, if supported
* View test details
* Return to dashboard
* Create another test

### Important states

* Code copied
* Copy failure
* Test creation failure

### Access requirements

Authenticated Teacher who created the test.

---

## TEACH-07 — Test Details

**Route:** `/teacher/tests/:testId`

**Primary role:** Teacher

### Purpose

Display information and activity related to a teacher-created test.

### Main content

* Test title
* Test description
* Test code
* Duration
* Number of questions
* Creation date
* Test status
* Student attempt count
* Result summary
* Proctoring alert summary

### Main actions

* Copy test code
* View test records
* View attempts
* View results
* View proctoring alerts
* Edit test, if editing is allowed
* Return to test records

### Important states

* Loading
* Test not found
* Test access denied
* No attempts
* No results
* No proctoring alerts

### Access requirements

Authenticated Teacher who owns the test.

---

## TEACH-08 — Attempts and Results

**Route:** `/teacher/tests/:testId/attempts`

**Primary role:** Teacher

### Purpose

Display student attempts and results for a teacher-created test.

### Main content

* Student name
* Attempt status
* Start time
* Submission time
* Score
* Result status
* Proctoring status
* Review status

### Main actions

* Search attempts
* Filter attempts
* View attempt details
* View result
* Open proctoring alerts

### Important states

* Loading
* No attempts
* No search results
* No flagged attempts
* Error loading attempts

### Access requirements

Authenticated Teacher who owns the test.

---

## TEACH-09 — Attempt / Proctoring Review

**Route:** `/teacher/attempts/:attemptId/review`

**Primary role:** Teacher / authorized reviewer

### Purpose

Allow an authorized teacher to inspect structured proctoring events related to a student attempt.

### Main content

* Student information
* Test information
* Attempt summary
* Submission status
* Score
* Proctoring event timeline
* Event type
* Event timestamp
* Event description
* Detection confidence, where applicable
* Review status
* Reviewer notes

### Main actions

* Filter events
* View event details
* Add review note
* Change review status
* Record permitted review decision
* Return to attempts

### Important states

* Events loading
* No events recorded
* Review already completed
* Review permission denied
* Save review failure

### Access requirements

Authenticated Teacher with permission to review the selected attempt.

The system must not automatically declare the student guilty based only on detected events.

---

## TEACH-10 — Teacher Profile

**Route:** `/teacher/profile`

**Primary role:** Teacher

### Purpose

Allow the teacher to view and update basic profile information.

### Main content

* Full name
* Email
* Profile photo, if implemented
* Account information
* Password-management option

### Main actions

* Edit profile
* Save changes
* Change password
* Logout

### Important states

* Loading
* Validation error
* Save success
* Save failure

### Access requirements

Authenticated Teacher only.

---

# 8. Admin Screens

## ADMIN-01 — Admin Dashboard

**Route:** `/admin/dashboard`

**Primary role:** Administrator

### Purpose

Provide a platform-level overview.

### Main content

* Total users
* Total students
* Total teachers
* Total tests
* Active tests
* Completed attempts
* Attempts requiring review
* Recent platform activity
* Basic system alerts

### Main actions

* Manage users
* Manage tests
* View proctoring alerts
* Open admin profile

### Important states

* Loading
* No activity
* Error loading dashboard

### Access requirements

Authenticated Admin only.

---

## ADMIN-02 — User Management

**Route:** `/admin/users`

**Primary role:** Administrator

### Purpose

Allow the admin to view and manage platform users.

### Main content

* User list
* Full name
* Email
* Role
* Account status
* Registration date

### Main actions

* Search users
* Filter users
* View user details
* Edit user
* Activate or deactivate account
* Change role, if permitted

### Important states

* Loading
* No users
* No search results
* User not found
* Action confirmation
* Action failure

### Access requirements

Authenticated Admin only.

---

## ADMIN-03 — User Details

**Route:** `/admin/users/:userId`

**Primary role:** Administrator

### Purpose

Display details and account information for a selected user.

### Main content

* User information
* Assigned role
* Account status
* Registration date
* Account activity
* Related tests or attempts, where authorized

### Main actions

* Edit user
* Change role, if permitted
* Activate or deactivate account
* Return to user list

### Important states

* Loading
* User not found
* Permission denied
* Action failure

### Access requirements

Authenticated Admin only.

---

## ADMIN-04 — Test Management

**Route:** `/admin/tests`

**Primary role:** Administrator

### Purpose

Allow the admin to view and manage platform tests.

### Main content

* Test list
* Test title
* Test creator
* Test code
* Creation date
* Test status
* Attempt count

### Main actions

* Search tests
* Filter tests
* View test details
* Manage test status
* View attempts
* View proctoring alerts

### Important states

* Loading
* No tests
* No search results
* Test not found
* Action confirmation
* Action failure

### Access requirements

Authenticated Admin only.

---

## ADMIN-05 — Test Details and Attempts

**Route:** `/admin/tests/:testId`

**Primary role:** Administrator

### Purpose

Display platform-level information about a selected test.

### Main content

* Test information
* Test creator
* Test code
* Duration
* Number of questions
* Test status
* Attempt count
* Result summary
* Proctoring alert summary

### Main actions

* View attempts
* View results
* View proctoring alerts
* Manage test status
* Return to test management

### Important states

* Loading
* Test not found
* No attempts
* No results
* No proctoring alerts

### Access requirements

Authenticated Admin only.

---

## ADMIN-06 — Proctoring Alerts

**Route:** `/admin/proctoring-alerts`

**Primary role:** Administrator

### Purpose

Display potentially suspicious proctoring events across the platform.

### Main content

* Alert list
* Test title
* Student name or candidate identifier
* Event type
* Event timestamp
* Attempt status
* Review status
* Basic severity or priority, if implemented

### Main actions

* Search alerts
* Filter alerts
* View alert details
* Open attempt review
* Update review status, if authorized

### Important states

* Loading
* No alerts
* No search results
* Alert not found
* Permission denied
* Save failure

### Access requirements

Authenticated Admin only.

---

## ADMIN-07 — Admin Profile

**Route:** `/admin/profile`

**Primary role:** Administrator

### Purpose

Allow the admin to view and update basic profile information.

### Main content

* Full name
* Email
* Profile photo, if implemented
* Account information
* Password-management option

### Main actions

* Edit profile
* Save changes
* Change password
* Logout

### Important states

* Loading
* Validation error
* Save success
* Save failure

### Access requirements

Authenticated Admin only.

---

# 9. Shared and System States

## SYS-01 — Not Found

**Route:** `*`

### Purpose

Display when a requested page or resource does not exist.

### Main content

* Not-found message
* Short explanation
* Return action

### Main actions

* Return to dashboard
* Return to home
* Go back

---

## SYS-02 — Unauthorized / Permission Denied

**Route:** `/unauthorized`

### Purpose

Inform a user that they do not have permission to access a requested resource.

### Main content

* Access-denied message
* Short explanation
* Appropriate return action

### Main actions

* Return to dashboard
* Return to previous page
* Go to login, if required

---

## SYS-03 — Global Error and Loading States

**Implementation:** Contextual states, not necessarily separate routes

### Included states

* Page loading
* Data loading
* Form submission loading
* Empty data
* Network error
* Server error
* Retry action
* Session expired
* Camera permission guidance
* Microphone permission guidance
* Fullscreen guidance
* Camera disconnected
* Microphone disconnected
* Network disconnected
* Auto-save failure

These states should be implemented as reusable components, banners, dialogs, inline messages, or full-page states depending on the situation.

They should not all become separate routes.

---

# 10. Screen Access Summary

| Screen Area              | Public |     Student |     Teacher |       Admin |
| ------------------------ | -----: | ----------: | ----------: | ----------: |
| Landing and public pages |    Yes |         Yes |         Yes |         Yes |
| Authentication           |    Yes |         Yes |         Yes |         Yes |
| Student dashboard        |     No |         Yes |          No |          No |
| Enter test code          |     No |         Yes |          No |          No |
| Student test details     |     No |         Yes |          No |          No |
| Student system check     |     No |         Yes |          No |          No |
| Student examination      |     No |         Yes |          No |          No |
| Student result/history   |     No |         Yes |          No |          No |
| Teacher dashboard        |     No |          No |         Yes |          No |
| Teacher test records     |     No |          No |         Yes |          No |
| Create test              |     No |          No |         Yes |          No |
| Teacher test details     |     No |          No |  Owner only |  Authorized |
| Teacher attempts/results |     No |          No |  Owner only |  Authorized |
| Proctoring review        |     No |          No |  Authorized |  Authorized |
| Admin dashboard          |     No |          No |          No |         Yes |
| User management          |     No |          No |          No |         Yes |
| Test management          |     No |          No |          No |         Yes |
| Admin proctoring alerts  |     No |          No |          No |         Yes |
| Profile screens          |     No | Own profile | Own profile | Own profile |

---

# 11. Interface Patterns That Should Not Become Separate Routes

The following features should normally be implemented as modals, drawers, tabs, or contextual states:

* Submission confirmation
* Delete-question confirmation
* Copy-code confirmation
* Camera permission guidance
* Microphone permission guidance
* Fullscreen guidance
* Network disconnected warning
* Camera disconnected warning
* Microphone disconnected warning
* Face-not-detected warning
* Multiple-face warning
* Tab-switch warning
* Session-expired notification
* Loading states
* Empty states
* Save-success messages
* Save-failure messages
* Test status confirmation
* Review decision confirmation

This reduces unnecessary navigation and keeps the application easier to build and maintain.

---

# 12. Screen Design Requirements

Every primary screen should define:

* Page title
* Primary purpose
* Main content
* Primary action
* Secondary actions
* Loading state
* Empty state, where applicable
* Error state
* Permission state, where applicable
* Responsive behavior
* Accessibility requirements

The final implementation should avoid creating unnecessary routes when a reusable interface pattern is more appropriate.

---

# 13. Screen Completion Criteria

The screen inventory will be considered complete when:

* All three user roles have defined interfaces.
* The public and authentication flows are covered.
* The Student dashboard is defined.
* The test-code access flow is defined.
* Test details and system checks are defined.
* Basic identity or face-presence verification is defined.
* The active examination interface is defined.
* Submission and automatic-submission states are defined.
* Result and examination-history screens are defined.
* The Teacher dashboard is defined.
* Test creation and MCQ addition are defined.
* Test preview and test-code success states are defined.
* Teacher test records and test details are defined.
* Attempts and proctoring review are defined.
* The Admin dashboard is defined.
* User and test management are defined.
* Admin proctoring alerts are defined.
* Profile screens are defined.
* Shared loading, error, permission, and empty states are documented.
* Every screen has a clear purpose and access requirement.

---

# 14. Final Scope Reminder

The first version of Proxam AI will not include:

* Public examination marketplace
* Student examination catalogue
* Complex question bank
* Separate question-selection workflow
* Candidate assignment management
* Complex scheduling interface
* Multiple-correct MCQs
* Descriptive questions
* Coding questions
* Continuous video recording
* Continuous audio recording
* Advanced biometric verification
* Advanced liveness detection
* Automatic cheating verdicts
* Complex role-permission editor
* Separate enterprise audit-log system
* Advanced analytics dashboard
* Native mobile application

The screen inventory must remain aligned with the simplified test-code-based application flow.
