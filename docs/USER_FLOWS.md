# Proxam AI — User Flows

## 1. Document Purpose

This document defines the major user journeys and system workflows for Proxam AI.

It explains how Students, Teachers/Examination Creators, and Administrators interact with the platform from beginning to end.

The purpose of this document is to:

* Define the expected user experience
* Identify required screens and transitions
* Clarify system responses
* Identify alternate and error conditions
* Support frontend development
* Support backend API planning
* Prevent missing steps during implementation
* Keep the application flow consistent with the finalized product scope

---

## 2. Primary User Roles

Proxam AI contains three primary roles:

1. Student
2. Teacher / Examination Creator
3. Administrator

Each role has a separate authorized workflow.

### 2.1 Student

Students can:

* Register and log in
* Enter a valid examination code
* View examination details
* Complete pre-exam system checks
* Complete basic identity or face-presence verification
* Attempt MCQ examinations
* Save and change answers
* Submit examinations
* View permitted results
* View their examination history
* Manage their profile

### 2.2 Teacher / Examination Creator

Teachers can:

* Log in
* View their dashboard
* Create MCQ examinations
* Add and edit questions
* Preview examinations
* Publish examinations
* Receive a unique examination code
* View their created examination records
* View examination details
* View student attempts and results
* Review available proctoring event metadata
* Manage their profile

### 2.3 Administrator

Administrators can:

* Log in
* View platform-level information
* Manage users
* View user details
* Manage examinations
* View examination attempts
* View authorized proctoring alerts
* Perform permitted administrative actions
* Manage their profile

---

# 3. General Application Flow

```text
User Opens Platform
        ↓
Landing Page
        ↓
Login / Registration
        ↓
Authentication
        ↓
Role Identification
        ↓
Role-Based Dashboard
        ↓
User Performs Authorized Actions
        ↓
Logout
```

The backend must identify the authenticated user's role and redirect the user to the correct dashboard.

The frontend must not rely only on hidden navigation items for authorization. The backend must enforce authentication and role-based access control.

---

# 4. Authentication Flows

## 4.1 Registration Flow

```text
Landing Page
        ↓
Click Register
        ↓
Registration Page
        ↓
Enter Name, Email, Password, and Required Details
        ↓
Frontend Validation
        ↓
Submit Registration
        ↓
Backend Validation
        ↓
Create User Account
        ↓
Registration Successful
        ↓
Redirect to Login
```

### Required registration validation

The system should validate:

* Required fields are present
* Email format is valid
* Email is not already registered
* Password meets minimum requirements
* Password confirmation matches
* Selected role is allowed for public registration

The first version should not allow users to register themselves as Administrators unless an approved administrative process is implemented.

### Possible alternate situations

* Email already exists
* Invalid email format
* Password is too weak
* Password confirmation does not match
* Required field is empty
* Registration request fails
* Network connection fails
* Account creation fails

The system should display a clear message and allow the user to correct the issue.

### Registration success behavior

After successful registration:

* The account should be created in the backend.
* The user should be redirected to Login.
* The system may display a confirmation message.
* Email verification may be added later if required.

---

## 4.2 Login Flow

```text
Login Page
        ↓
Enter Email and Password
        ↓
Submit Login
        ↓
Backend Validates Credentials
        ↓
Identify User Role
        ↓
Create Authenticated Session
        ↓
Redirect to Role-Based Dashboard
```

### Role-based redirection

```text
Successful Login
        ├── Student → Student Dashboard
        ├── Teacher → Teacher Dashboard
        └── Administrator → Admin Dashboard
```

### Possible alternate situations

* Incorrect email or password
* Account is inactive
* Account is blocked
* Account is not verified, if verification is implemented
* Session creation fails
* Network error
* Server error
* User attempts to access a dashboard belonging to another role

The system should not reveal whether a specific email address exists when that would create a security risk.

---

## 4.3 Logout Flow

```text
Any Authenticated Page
        ↓
Open User Menu
        ↓
Click Logout
        ↓
Invalidate Authenticated Session
        ↓
Clear Local Session State
        ↓
Redirect to Login or Landing Page
```

The backend should invalidate the session or authentication token according to the selected authentication implementation.

---

## 4.4 Session Expiration Flow

```text
Authenticated User
        ↓
Session Expires
        ↓
Frontend or Backend Detects Expired Session
        ↓
Display Session Expired Message
        ↓
Redirect to Login
```

During an active examination, session expiration must be handled carefully.

The system should:

* Preserve already confirmed answers where possible
* Avoid silently losing the current examination state
* Display a clear recovery message
* Prevent unauthorized continuation after the session is invalid

---

# 5. Student User Flows

## 5.1 Student Dashboard Flow

```text
Student Login
        ↓
Student Dashboard
        ↓
View Student Information
        ↓
View Examination Records
        ↓
Choose an Action
        ├── Enter Test Code
        ├── View Previous Examination
        └── Open Student Profile
```

The Student Dashboard should contain:

* Brief student information
* Enter Code button
* Examination history or records
* Recently attempted examinations, if available
* Profile avatar or user menu

The student should not see examinations that they have not accessed through a valid examination code.

---

## 5.2 Enter Test Code Flow

This is the primary method through which students access examinations.

```text
Student Dashboard
        ↓
Click Enter Code
        ↓
Enter Examination Code
        ↓
Frontend Validates Code Format
        ↓
Send Code to Backend
        ↓
Backend Validates Examination Code
        ↓
Valid Code?
        ├── No → Display Error Message
        └── Yes → Load Examination Details
```

### Example code format

```text
PXAM-7K4Q2
```

The exact code format will be finalized during backend implementation.

### Possible failure situations

* Code field is empty
* Code format is invalid
* Code does not exist
* Examination is inactive
* Examination has expired
* Examination is not yet available
* Student is not allowed to access the examination
* Student has already used the permitted attempt
* Network request fails

The system should not reveal unnecessary internal information about invalid codes.

---

## 5.3 View Examination Details Flow

```text
Valid Examination Code
        ↓
Examination Details Page
        ↓
View Examination Information
        ↓
Read Instructions
        ↓
Check Duration and Marks
        ↓
Check Examination Availability
        ↓
Check Proctoring Requirements
        ↓
Click Start Examination
```

The examination details page may display:

* Examination title
* Teacher or examination creator
* Number of questions
* Total marks
* Duration
* Examination instructions
* Attempt restrictions
* Proctoring requirements
* Examination availability
* Result publication information, if applicable

### Backend checks

Before allowing the student to continue, the backend should verify:

* The examination exists
* The examination code is valid
* The examination is published
* The examination is currently available
* The student is eligible to attempt it
* The student has not exceeded the allowed attempts
* The examination has not expired

If any requirement fails, the student should see an appropriate message instead of entering the examination.

---

## 5.4 Start Examination Flow

```text
Examination Details
        ↓
Click Start Examination
        ↓
Display Pre-Exam Instructions
        ↓
Pre-Exam System Check
        ↓
Basic Identity / Face-Presence Verification
        ↓
Backend Rechecks Eligibility
        ↓
Create Examination Attempt
        ↓
Initialize Official Timer
        ↓
Load Examination Questions
        ↓
Enter Active Examination
```

The examination attempt should be created according to the finalized attempt-creation policy.

For the first version, the recommended approach is:

* Perform basic checks first.
* Confirm examination eligibility.
* Create the official attempt on the backend.
* Start the official timer using backend-controlled time.
* Enter the active examination interface.

---

## 5.5 Pre-Exam System Check Flow

```text
Pre-Exam System Check Page
        ↓
Check Browser Compatibility
        ↓
Check Camera Permission
        ↓
Check Microphone Permission
        ↓
Check Camera Availability
        ↓
Check Microphone Availability
        ↓
Check Network Connection
        ↓
Check Fullscreen Capability
        ↓
Display Check Results
        ↓
All Required Checks Passed?
        ├── No → Display Issue and Retry Instructions
        └── Yes → Continue to Identity / Face-Presence Verification
```

### Checks included in the first version

* Browser compatibility
* Camera permission
* Camera availability
* Microphone permission
* Microphone availability
* Network connection
* Fullscreen capability

### Possible failure situations

* Camera permission denied
* Microphone permission denied
* Camera not detected
* Microphone not detected
* Another application is using the camera
* Browser does not support required features
* Network connection is unstable
* Fullscreen is unavailable
* User closes or blocks a permission prompt
* Camera or microphone permission changes during the check

The system should provide troubleshooting guidance rather than displaying only a technical error.

### Example recovery guidance

* Allow camera permission in browser settings.
* Allow microphone permission in browser settings.
* Close another application using the camera.
* Refresh the page and retry the check.
* Use a supported browser.
* Check the network connection.
* Move to a location with better lighting for face verification.

---

## 5.6 Basic Identity / Face-Presence Verification Flow

The first version should use a limited verification workflow.

It should not promise advanced biometric identification, advanced liveness detection, or highly accurate identity matching unless those capabilities are actually implemented.

```text
Pre-Exam Checks Passed
        ↓
Identity / Face-Presence Verification Page
        ↓
Display Verification Instructions
        ↓
Access Camera Feed
        ↓
Detect Face Presence
        ↓
Check Basic Face Visibility
        ↓
Verification Successful?
        ├── No → Display Reason and Retry
        └── Yes → Continue to Attempt Creation
```

### Possible outcomes

* Face detected successfully
* No face detected
* Face is unclear
* Face is outside the camera frame
* Poor lighting
* Camera unavailable
* Verification service unavailable
* Maximum retry limit reached

The system should display simple user-facing messages.

It should not expose unnecessary biometric data, internal confidence values, or technical model information to the student.

---

## 5.7 Examination Attempt Creation Flow

```text
Required Pre-Exam Checks Passed
        ↓
Basic Identity / Face-Presence Verification Completed
        ↓
Backend Verifies Student Eligibility
        ↓
Backend Verifies Examination Availability
        ↓
Backend Checks Previous Attempts
        ↓
Create Attempt Record
        ↓
Assign Attempt ID
        ↓
Set Official Start Time
        ↓
Calculate Permitted End Time
        ↓
Load Correct Question Set
        ↓
Enter Active Examination
```

The backend should be responsible for:

* Creating the official attempt record
* Assigning the attempt ID
* Setting the examination start time
* Calculating the permitted end time
* Loading the correct question set
* Preventing unauthorized duplicate attempts
* Enforcing attempt limits
* Enforcing examination availability

The frontend should not independently decide the official examination start time.

---

## 5.8 Active Examination Flow

```text
Active Examination
        ↓
Display Current Question
        ↓
Student Selects or Changes Answer
        ↓
Save Answer
        ↓
Student Navigates Questions
        ↓
System Monitors Selected Signals
        ↓
Potential Event Detected?
        ├── No → Continue Examination
        └── Yes → Record Event Metadata
        ↓
Student Continues Until Submission or Time Expiry
```

During the examination, the system should:

* Display the remaining time
* Display the current question
* Display available question navigation
* Preserve selected answers
* Allow students to change answers
* Allow students to move between questions
* Allow marking questions for review
* Save answers automatically where possible
* Monitor configured browser and device signals
* Display relevant warnings
* Record potentially suspicious event metadata
* Prevent unauthorized application routes from being accessed

The active examination interface should include:

* Question area
* Answer options
* Question navigation
* Answered and unanswered indicators
* Mark-for-review state
* Remaining timer
* Save or synchronization status
* Small monitoring preview or monitoring status
* Submit Examination action

---

## 5.9 Answer Saving Flow

```text
Student Selects Answer
        ↓
Frontend Updates Selected Option
        ↓
Send Answer-Save Request
        ↓
Backend Validates Attempt
        ↓
Backend Validates Question and Option
        ↓
Backend Saves Answer
        ↓
Backend Confirms Save
        ↓
Frontend Displays Saved Status
```

The frontend must not falsely display that an answer has been saved if the backend has not confirmed it.

### Possible alternate situations

* Network temporarily unavailable
* Answer-save request fails
* Attempt has expired
* Attempt is already submitted
* Session has expired
* Question is no longer available
* Backend validation fails

### Recommended answer states

* Not answered
* Saving
* Saved
* Save failed
* Pending synchronization

If saving fails, the interface should:

* Display a clear warning
* Preserve the answer locally where possible
* Retry the request
* Avoid silently discarding the selected answer
* Inform the student if the answer has not yet reached the server

---

## 5.10 Question Navigation Flow

```text
Current Question
        ↓
Student Selects Navigation Action
        ├── Next Question
        ├── Previous Question
        ├── Question Palette
        └── Mark for Review
        ↓
Save Current Answer if Necessary
        ↓
Load Selected Question
        ↓
Display Existing Answer and Question State
```

The system should preserve:

* Selected answer
* Answered state
* Mark-for-review state
* Current question position

The question palette should clearly distinguish between:

* Answered questions
* Unanswered questions
* Questions marked for review
* Current question

---

## 5.11 Proctoring Monitoring Flow

```text
Monitoring Signal
        ↓
Detection Logic
        ↓
Potentially Suspicious Condition Identified
        ↓
Validate Event Conditions
        ↓
Create Event Metadata
        ↓
Associate Event with Attempt
        ↓
Update Attempt Proctoring Status
        ↓
Make Event Available for Authorized Review
```

### Possible event types

* Face not detected
* Multiple faces detected
* Looking away detected
* Camera disconnected
* Microphone disconnected
* Tab visibility changed
* Fullscreen exited
* Repeated browser-session interruptions
* Network interruption

### Event metadata may include

* Event ID
* Attempt ID
* Student ID
* Event type
* Timestamp
* Detection confidence, where applicable
* Event description
* Review status

The system should distinguish between:

1. A detected signal
2. A recorded event
3. A review decision

The system must not automatically classify the student as guilty of cheating.

---

## 5.12 Fullscreen Exit Flow

```text
Active Examination
        ↓
Fullscreen Exit Detected
        ↓
Record Event Metadata
        ↓
Display Warning
        ↓
Student Returns to Fullscreen?
        ├── Yes → Continue Examination
        └── No → Maintain Warning or Apply Configured Policy
```

The first version should preferably use:

* Warning display
* Event recording
* Requirement to return to fullscreen
* Escalation of repeated events for authorized review

The exact policy must be finalized before implementation.

The system should not automatically terminate an examination solely because of one fullscreen exit unless that behavior is explicitly approved.

---

## 5.13 Tab-Switch Flow

```text
Active Examination
        ↓
Examination Tab Becomes Inactive
        ↓
Record Visibility Event
        ↓
Display Warning When Student Returns
        ↓
Student Continues Examination
```

The system should not claim that every tab switch proves cheating because browser visibility changes can occur for legitimate reasons.

Possible legitimate causes include:

* Operating-system notifications
* Accidental tab changes
* Browser permission prompts
* Network or browser behavior
* User interaction outside the examination tab

Repeated events may be made available for authorized review.

---

## 5.14 Camera or Microphone Disconnection Flow

```text
Active Examination
        ↓
Camera or Microphone Disconnection Detected
        ↓
Record Event Metadata
        ↓
Display Clear Warning
        ↓
Attempt to Reconnect or Restore Permission
        ↓
Connection Restored?
        ├── Yes → Continue Monitoring
        └── No → Apply Configured Examination Policy
```

The warning should explain:

* Which device is unavailable
* Whether the student can continue temporarily
* How to restore permission or connection
* Whether the event has been recorded

The first version should avoid automatically declaring the attempt invalid solely because of a temporary device interruption.

---

## 5.15 Network Disconnection Flow

```text
Active Examination
        ↓
Network Disconnection Detected
        ↓
Display Connection Warning
        ↓
Preserve Current Local State Where Possible
        ↓
Retry Connection
        ↓
Connection Restored?
        ├── No → Continue Safe Recovery Attempts
        └── Yes → Synchronize Pending Data
        ↓
Display Synchronization Status
```

The final implementation must define:

* Whether the timer continues during disconnection
* Whether the student can continue answering
* How long temporary disconnection is tolerated
* How pending answers are synchronized
* What happens if the examination ends while disconnected

The recommended first-version policy is:

* The official timer continues according to backend time.
* Previously confirmed answers remain stored on the server.
* Unsynchronized answers are preserved locally where possible.
* The interface clearly displays synchronization status.
* The attempt is not automatically marked as cheating because of network failure.

---

## 5.16 Manual Submission Flow

```text
Active Examination
        ↓
Student Clicks Submit
        ↓
Display Submission Confirmation
        ↓
Show Answered / Unanswered / Marked Questions
        ↓
Student Confirms Submission
        ↓
Backend Validates Attempt Status
        ↓
Save Final Answers
        ↓
Finalize Attempt
        ↓
Stop Timer and Monitoring
        ↓
Evaluate Answers
        ↓
Display Examination Submitted Screen
```

The student should have an opportunity to return to the examination before confirming submission.

### Submission validation

The backend should verify:

* Attempt belongs to the authenticated student
* Attempt is still in progress
* Attempt has not already been submitted
* Final answers are valid
* Examination has not already expired

---

## 5.17 Automatic Submission Flow

```text
Active Examination
        ↓
Official Timer Reaches Zero
        ↓
Disable Further Answer Changes
        ↓
Save Available Confirmed Answers
        ↓
Finalize Attempt
        ↓
Stop Timer and Monitoring
        ↓
Evaluate Answers
        ↓
Display Automatic Submission Message
```

Automatic submission should be controlled by the backend according to the official examination end time.

The frontend timer is only a display. It must not be treated as the final authority for examination expiry.

---

## 5.18 Examination Submitted Flow

```text
Attempt Submitted
        ↓
Stop Active Examination Interface
        ↓
Stop Monitoring Interface
        ↓
Display Submission Confirmation
        ↓
Show Submission Time and Attempt Status
        ↓
Provide Result Access When Available
        ↓
Return to Student Dashboard or Result Page
```

The submitted screen may display:

* Examination title
* Submission status
* Submission time
* Whether the attempt was submitted manually or automatically
* Result availability status
* Button to view result, if published
* Button to return to dashboard

---

## 5.19 Examination Result Flow

```text
Attempt Submitted
        ↓
Evaluate MCQ Answers
        ↓
Calculate Score
        ↓
Generate Result
        ↓
Check Result Publication Settings
        ↓
Result Published?
        ├── No → Display Result Pending
        └── Yes → Display Permitted Result Details
```

For the first version, MCQ evaluation should be automatic.

A result may contain:

* Examination title
* Student name
* Total questions
* Attempted questions
* Correct answers
* Incorrect answers
* Unanswered questions
* Total marks
* Obtained marks
* Percentage, if required
* Submission time
* Result status

### Possible result states

* Evaluation pending
* Result generated
* Result published
* Result restricted
* Result withheld
* Result under review

The student should not see internal proctoring notes or restricted administrative decisions.

---

## 5.20 Student Examination History Flow

```text
Student Dashboard
        ↓
Open Examination Records / History
        ↓
View Previous Attempts
        ↓
Select an Attempt
        ↓
View Permitted Attempt Details
        ↓
View Result, if Available
```

Students should only be able to access their own examination records.

Students should not be able to access:

* Other students' attempts
* Internal teacher notes
* Internal administrative notes
* Restricted proctoring event details
* Private review decisions
* Backend implementation information

---

## 5.21 Student Profile Flow

```text
Student Dashboard
        ↓
Click Profile Avatar
        ↓
Open Student Profile
        ↓
View Account Information
        ↓
Edit Allowed Profile Details
        ↓
Save Changes
```

The profile page may include:

* Name
* Email
* Profile image, if implemented
* Account creation information
* Basic account settings

The student should not be able to change protected fields or assign themselves a different role.

---

# 6. Teacher User Flows

## 6.1 Teacher Dashboard Flow

```text
Teacher Login
        ↓
Teacher Dashboard
        ↓
View Teacher Information
        ↓
View Created Examination Records
        ↓
Choose an Action
        ├── Create Test
        ├── Open Test Record
        └── Open Teacher Profile
```

The Teacher Dashboard should contain:

* Brief teacher information
* Create Test button
* Created examination records
* Examination status
* Test code, where available
* Profile avatar or user menu

---

## 6.2 Create Test — Test Details Flow

```text
Teacher Dashboard
        ↓
Click Create Test
        ↓
Create Test Page
        ↓
Enter Test Title
        ↓
Enter Description or Instructions
        ↓
Configure Duration
        ↓
Configure Total Marks or Question Marks
        ↓
Configure Basic Examination Rules
        ↓
Continue to Add Questions
```

### Possible test details

* Test title
* Test description
* Instructions
* Duration
* Marks per question
* Negative marking, only if implemented
* Basic proctoring requirements
* Result publication behavior, if required

The first version should avoid unnecessary configuration complexity.

---

## 6.3 Add MCQ Questions Flow

Teachers should create questions directly inside the test creation process.

```text
Create Test — Test Details
        ↓
Open Add Questions Step
        ↓
Click Add Question
        ↓
Enter Question Text
        ↓
Enter Answer Options
        ↓
Select Correct Answer
        ↓
Enter Marks
        ↓
Validate Question
        ↓
Save Question
        ↓
Display Question in Test Question List
```

### First-version question format

Each question should contain:

* Question text
* Four answer options, unless another number is finalized
* One correct answer
* Marks

Optional fields may include:

* Explanation
* Question image
* Question difficulty

Optional fields should not delay the basic implementation.

### Possible errors

* Empty question text
* Empty option
* Duplicate option
* No correct answer selected
* More than one correct answer selected
* Invalid marks
* Incomplete question
* Question list contains no valid questions

The system should allow the teacher to:

* Add a question
* Edit a question
* Delete a question
* Reorder questions
* Review all added questions

A separate reusable Question Bank is not required for the first version.

---

## 6.4 Test Preview Flow

```text
Create Test
        ↓
Test Details Completed
        ↓
Questions Added
        ↓
Click Preview Test
        ↓
Display Student-Like Examination Preview
        ↓
Teacher Reviews Details and Questions
        ↓
Teacher Returns to Edit or Continues
```

The preview should show:

* Test title
* Instructions
* Duration
* Question count
* Question text
* Answer options
* Correct answer indication for the teacher
* Question order

The correct answer should not be visible in the student-facing preview mode.

---

## 6.5 Create Test Validation Flow

```text
Test Preview
        ↓
Click Create Test
        ↓
Frontend Validates Required Fields
        ↓
Backend Validates Test Details
        ↓
Backend Validates Question Set
        ↓
Backend Creates Test
        ↓
Backend Generates Unique Test Code
        ↓
Display Test Creation Success
```

The backend should validate:

* Test title is present
* Duration is valid
* At least one question exists
* Every question has valid options
* Every question has one correct answer
* Marks are valid
* Teacher is authenticated
* Teacher is authorized to create the test

---

## 6.6 Test Code Generation and Success Flow

```text
Test Successfully Created
        ↓
Backend Generates Unique Test Code
        ↓
Associate Code with Test
        ↓
Display Success Screen or Modal
        ↓
Show Test Code
        ↓
Teacher Copies or Shares Code
        ↓
Return to Teacher Dashboard or Test Details
```

Example:

```text
PXAM-7K4Q2
```

The test code should:

* Be unique
* Be associated with one examination
* Be validated by the backend
* Not expose internal database IDs
* Be easy to copy
* Be displayed clearly after test creation

The success interface may include:

* Test title
* Test code
* Copy Code button
* Share Code action, if implemented
* View Test button
* Return to Dashboard button

---

## 6.7 Teacher Test Records Flow

```text
Teacher Dashboard
        ↓
View Test Records
        ↓
Select a Test
        ↓
Open Test Details
```

Teacher test records may display:

* Test title
* Test code
* Creation date
* Test status
* Number of questions
* Duration
* Number of attempts
* Result status

The teacher should only see examinations created by that teacher unless the user is an Administrator.

---

## 6.8 Teacher Test Details Flow

```text
Teacher Dashboard
        ↓
Select Created Test
        ↓
Open Test Details
        ↓
View Test Information
        ↓
View Questions
        ↓
View Test Code
        ↓
View Attempts and Results
```

The Test Details page may provide:

* Test title
* Description
* Duration
* Marks
* Questions
* Test code
* Publication status
* Attempt count
* Result information
* Proctoring status

Permitted actions may include:

* View test
* Edit test before attempts begin
* View attempts
* View results
* Copy test code
* Archive test, if implemented

---

## 6.9 Teacher Attempts and Results Flow

```text
Teacher Dashboard
        ↓
Open Created Test
        ↓
Open Attempts or Results
        ↓
View Attempt List
        ↓
Select Attempt
        ↓
View Attempt Details
```

Attempt details may include:

* Student name
* Attempt ID
* Start time
* Submission time
* Attempt status
* Score
* Result status
* Proctoring status
* Review status

The teacher should not see information belonging to examinations created by other teachers unless authorized.

---

## 6.10 Teacher Proctoring Review Flow

```text
Teacher Dashboard
        ↓
Open Created Test
        ↓
Open Attempts
        ↓
Select an Attempt
        ↓
Open Proctoring Review
        ↓
View Attempt Summary
        ↓
View Event Timeline
        ↓
Inspect Event Details
        ↓
Add Reviewer Notes, if permitted
        ↓
Record Permitted Review Decision
        ↓
Save Review
        ↓
Update Review Status
```

The review interface may include:

* Student information
* Attempt status
* Submission time
* Proctoring status
* Event timeline
* Event type
* Event timestamp
* Event description
* Review notes
* Review status

The system should not automatically label an attempt as cheating based only on detection events.

The teacher's decision authority must be defined by the approved permission policy.

---

## 6.11 Teacher Profile Flow

```text
Teacher Dashboard
        ↓
Click Profile Avatar
        ↓
Open Teacher Profile
        ↓
View Account Information
        ↓
Edit Allowed Profile Details
        ↓
Save Changes
```

The profile page may include:

* Name
* Email
* Profile image, if implemented
* Account information
* Basic account settings

---

# 7. Administrator User Flows

## 7.1 Admin Dashboard Flow

```text
Admin Login
        ↓
Admin Dashboard
        ↓
View Platform Summary
        ↓
Choose an Administrative Action
        ├── Manage Users
        ├── Manage Tests
        ├── View Proctoring Alerts
        └── Open Admin Profile
```

The first version should keep the Admin Panel focused on essential management tasks.

---

## 7.2 User Management Flow

```text
Admin Dashboard
        ↓
Open User Management
        ↓
Search or Filter Users
        ↓
Select User
        ↓
View User Details
        ↓
Perform Authorized Action
        ↓
Confirm Action
        ↓
Save Changes
```

Possible actions may include:

* View user
* Change account status
* Activate or deactivate account
* View user's role
* View related examinations or attempts
* Update permitted account details

Role changes should be restricted and carefully validated.

The system should not provide an unrestricted permission editor in the first version unless it is required.

---

## 7.3 User Details Flow

```text
User Management
        ↓
Select User
        ↓
Open User Details
        ↓
View Account Information
        ↓
View Role and Status
        ↓
View Related Activity, if Authorized
        ↓
Perform Permitted Action
```

The page may display:

* Name
* Email
* Role
* Account status
* Registration date
* Related tests or attempts, where permitted

Sensitive information should only be displayed to authorized administrators.

---

## 7.4 Test Management Flow

```text
Admin Dashboard
        ↓
Open Test Management
        ↓
Search or Filter Tests
        ↓
Select Test
        ↓
View Test Details
        ↓
View Attempts and Results
        ↓
Perform Authorized Administrative Action
```

Possible actions may include:

* View test
* View test creator
* View test status
* View test code
* View attempts
* View results
* Archive test, if implemented
* Change permitted test status

The Administrator should not modify examination data casually after students have started attempting the examination.

---

## 7.5 Proctoring Alerts Flow

```text
Admin Dashboard
        ↓
Open Proctoring Alerts
        ↓
View Recorded Events
        ↓
Filter by Test, Student, Event Type, or Date
        ↓
Select an Event or Attempt
        ↓
View Event Details
        ↓
Perform Authorized Review Action
```

The Proctoring Alerts page may display:

* Attempt ID
* Test title
* Student
* Event type
* Event timestamp
* Event description
* Review status

The system should distinguish between:

* A recorded event
* A review status
* A final administrative decision

The page should not automatically describe a student as guilty of cheating.

---

## 7.6 Admin Profile Flow

```text
Admin Dashboard
        ↓
Click Profile Avatar
        ↓
Open Admin Profile
        ↓
View Account Information
        ↓
Edit Allowed Profile Details
        ↓
Save Changes
```

---

# 8. Shared System Flows

## 8.1 Unauthorized Access Flow

```text
User Requests Protected Resource
        ↓
Check Authentication
        ↓
Check Role and Permission
        ↓
Authorized?
        ├── Yes → Load Resource
        └── No → Display Unauthorized Page
```

The backend must enforce authorization even if the frontend hides unauthorized navigation items.

Examples:

* Student attempts to open Teacher Dashboard
* Teacher attempts to open Admin Panel
* Student attempts to view another student's result
* Teacher attempts to edit another teacher's test
* Unauthenticated user attempts to access an examination attempt

---

## 8.2 Notification Flow

The first version should keep notifications simple.

```text
System Event
        ↓
Determine Notification Requirement
        ↓
Create Notification or Status Message
        ↓
Display Notification
        ↓
User Views Notification
```

Possible notifications include:

* Test created successfully
* Test code generated
* Examination result published
* Account status changed
* Proctoring review status updated
* Session expired
* Network synchronization failed
* System error
* Examination submitted successfully

Email notifications are optional and should not be treated as a required first-version feature.

---

## 8.3 Error Recovery Flow

```text
User Performs Action
        ↓
Request Fails
        ↓
Display Clear Error Message
        ↓
Provide Retry or Correction Action
        ↓
User Retries
        ↓
Request Succeeds or Error Persists
```

The system should:

* Use understandable error messages
* Avoid exposing stack traces
* Avoid exposing database errors
* Preserve user input where possible
* Provide a retry action for temporary failures
* Redirect to a safe page when recovery is not possible

---

## 8.4 Loading State Flow

```text
User Performs Action
        ↓
Request Begins
        ↓
Display Loading State
        ↓
Request Completes
        ├── Success → Display Result
        └── Failure → Display Error and Retry Option
```

Loading states should be provided for:

* Login
* Registration
* Test-code validation
* Test creation
* Question saving
* Answer saving
* Result loading
* Profile updates
* Admin actions

---

## 8.5 Empty State Flow

```text
User Opens a Page
        ↓
No Data Available
        ↓
Display Empty State
        ↓
Explain the Situation
        ↓
Provide Relevant Next Action
```

Examples:

* No examination records
* No created tests
* No student attempts
* No proctoring alerts
* No search results

Empty states should not look like system errors.

---

# 9. Important State Transitions

## 9.1 Examination State

```text
Draft
    ↓
Published
    ↓
Active
    ↓
Completed
    ↓
Archived
```

### State descriptions

* **Draft:** Test is being created or edited and is not available to students.
* **Published:** Test is available through its valid code according to its rules.
* **Active:** Test can currently be attempted.
* **Completed:** Test is no longer accepting attempts.
* **Archived:** Test is retained for records but is no longer active.

The exact state names and transitions will be finalized during backend planning.

---

## 9.2 Attempt State

```text
Not Started
    ↓
In Progress
    ├── Submitted
    ├── Auto-Submitted
    ├── Abandoned
    └── Expired
            ↓
        Evaluated
            ↓
      Result Generated
```

An attempt may also enter a review state:

```text
Result Generated
        ↓
Under Review
        ↓
Reviewed
        ↓
Decision Recorded
```

### State descriptions

* **Not Started:** Student has not created an attempt.
* **In Progress:** Student is currently attempting the examination.
* **Submitted:** Student manually submitted the examination.
* **Auto-Submitted:** System submitted the examination after the official timer ended.
* **Abandoned:** Attempt was left incomplete according to the configured policy.
* **Expired:** Attempt passed its permitted end time.
* **Evaluated:** MCQ answers have been checked.
* **Result Generated:** Score and result data have been calculated.
* **Under Review:** Authorized review is taking place.
* **Reviewed:** Review has been completed.
* **Decision Recorded:** An authorized final review decision has been stored.

---

## 9.3 Proctoring Review State

```text
No Review Required
        ↓
Flagged
        ↓
Unreviewed
        ↓
Under Review
        ↓
Reviewed
        ↓
Decision Recorded
```

The exact status names will be finalized during feature and database planning.

A recorded proctoring event must not automatically mean that the student has cheated.

---

# 10. Flow Design Principles

All workflows should follow these principles:

* Users should always know what step they are currently on.
* Important actions should require clear confirmation.
* Errors should explain how to recover.
* Destructive actions should require confirmation.
* Examination data should be saved reliably.
* Students should not be automatically accused based on detection events.
* Sensitive information should be visible only to authorized users.
* The system should distinguish between a warning, a recorded event, and a final decision.
* The frontend should not assume that a request succeeded without backend confirmation.
* The backend should be the authority for examination eligibility, attempt status, timer, and submission.
* Test codes should be generated and validated by the backend.
* Students should access examinations through valid test codes.
* Teachers should create MCQs directly inside the test-creation workflow.
* The first version should avoid unnecessary enterprise-level complexity.
* Every important administrative or review action should be auditable where required.
* Temporary technical failures should not automatically be treated as misconduct.
* The interface should provide clear loading, empty, success, and error states.

---

# 11. Flow Completion Criteria

The user-flow specification will be considered complete when:

* Student registration and login flows are defined.
* Role-based authentication and redirection are defined.
* Students can enter a test code.
* Test-code validation and failure conditions are defined.
* Students can view examination details.
* Pre-exam system checks are included.
* Basic identity or face-presence verification is included.
* The complete examination attempt flow is defined.
* Answer saving and question navigation behavior are defined.
* Proctoring event recording is defined.
* Fullscreen, tab-switch, device, and network interruption flows are defined.
* Manual and automatic submission flows are defined.
* Result generation and publication states are defined.
* Student examination history is defined.
* Teachers can create test details.
* Teachers can add, edit, delete, and reorder MCQ questions.
* Teachers can preview and create examinations.
* Backend-generated test-code flow is defined.
* Teachers can view created test records.
* Teachers can view attempts and results.
* Teacher proctoring review is defined.
* Administrators can manage users.
* Administrators can manage examinations.
* Administrators can view authorized proctoring alerts.
* Shared session, authorization, notification, loading, empty, and error flows are defined.
* Important examination, attempt, and review states are documented.
* The flows do not depend on features excluded from the first version.

---

# 12. Features Explicitly Excluded from the First-Version Flows

The following features are not required for the first version unless separately approved:

* Public examination marketplace
* Student examination catalogue
* Separate reusable question bank
* Complex candidate assignment system
* Bulk candidate import
* Advanced examination scheduling
* Multiple-correct MCQs
* Descriptive questions
* Coding questions
* Continuous video recording
* Continuous audio recording
* Advanced biometric identity verification
* Advanced liveness detection
* Automatic cheating verdicts
* Complex live monitoring wall
* Advanced analytics
* Payment or subscription features
* Native mobile applications
* Complex role-permission editor
* Enterprise-level notification system
* Advanced offline examination mode
* Microservices architecture
