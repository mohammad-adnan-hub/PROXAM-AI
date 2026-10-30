# Proxam AI

## 1. Project Overview

**Proxam AI** is a browser-based online examination platform designed to help teachers and educational organizations conduct organized, MCQ-based examinations.

The platform combines a complete online examination workflow with AI-assisted proctoring. Teachers can create tests, add multiple-choice questions, and generate a unique test code. Students can enter this code to access the test, complete the required pre-exam checks, attempt the examination, and view their results.

During an examination, the system monitors selected webcam, microphone, browser, and session-related signals. These signals are used to identify potentially suspicious events such as face absence, multiple faces, looking away, tab switching, or exiting fullscreen mode.

Proxam AI does not automatically declare a student guilty of cheating. It records potentially suspicious events as structured metadata and allows authorized users to review them. Final decisions remain the responsibility of authorized human reviewers.

The first version will focus on a simple, functional, and realistic examination workflow rather than a large enterprise examination-management system.

---

## 2. Problem Statement

Traditional examinations require physical infrastructure, manual supervision, and considerable administrative effort.

Online examinations provide flexibility, but they also create several challenges:

* Maintaining examination integrity in remote environments
* Verifying that the correct student is attempting the examination
* Monitoring suspicious examination-related behavior
* Creating and managing examination questions
* Preventing unauthorized access to tests
* Evaluating answers efficiently
* Providing results to students
* Handling technical issues during an active examination
* Reviewing potentially suspicious examination events

Many basic online quiz platforms mainly focus on displaying questions and calculating scores. They may not provide a complete workflow involving authentication, test-code access, pre-exam checks, browser monitoring, event recording, and result generation.

Proxam AI aims to address these challenges through one integrated platform.

---

## 3. Proposed Solution

Proxam AI will provide a centralized platform with three primary roles:

1. Student
2. Teacher or Examination Creator
3. Admin

Teachers will be able to create MCQ-based tests by entering test details and adding questions. After creating a test, the system will generate a unique test code.

Students will use the test code to access the examination. Before starting, they will complete the required instructions and system checks. During the examination, the platform will display questions, manage the timer, save answers, and monitor selected examination-related signals.

After submission, the system will automatically evaluate the objective answers and generate the result.

Potentially suspicious proctoring events will be stored as structured metadata for authorized review. The system will support human review rather than automatically deciding whether cheating occurred.

---

## 4. Project Objectives

The main objectives of Proxam AI are:

* To create a functional browser-based online examination platform
* To support MCQ-based examinations
* To provide separate workflows for Students, Teachers, and Admins
* To allow teachers to create tests and add questions
* To generate a unique test code for each examination
* To allow students to access tests through a valid test code
* To provide a simple and reliable examination interface
* To perform pre-exam system checks
* To perform a basic identity or face-presence verification step
* To monitor selected webcam and microphone signals
* To detect potentially suspicious examination events
* To monitor fullscreen and tab-switch activity
* To save structured proctoring event metadata
* To automatically evaluate single-correct MCQ answers
* To generate examination results
* To provide students with examination history
* To allow authorized users to review flagged examination attempts
* To maintain role-based access to examination and proctoring data
* To demonstrate the integration of web development, databases, authentication, and AI-assisted monitoring

---

## 5. Target Users

Proxam AI is intended for general examination use by:

* Colleges and universities
* Schools and educational institutions
* Coaching and training institutes
* Professional training providers
* Organizations conducting internal assessments
* Teachers conducting online tests
* Small educational teams requiring a controlled MCQ examination platform

The first version will focus on a manageable examination workflow rather than large-scale commercial deployment.

---

## 6. User Roles

The first version will contain three primary user roles.

### 6.1 Student

Students can:

* Register and log in
* Access the student dashboard
* Enter a valid test code
* View basic test information
* Read examination instructions
* Complete pre-exam system checks
* Complete the basic identity or face-presence verification step
* Start an examination
* Answer MCQ questions
* Navigate between questions
* Clear selected answers
* Mark questions for review
* View the question palette
* Submit an examination
* View examination results
* View examination history
* Manage their profile information

Students cannot:

* Create tests
* Edit tests
* View other students' results
* Access teacher or admin features
* View private proctoring records belonging to other students

### 6.2 Teacher / Examination Creator

Teachers or examination creators can:

* Register and log in
* Access the teacher dashboard
* Create a new test
* Enter test details
* Add single-correct MCQ questions
* Add answer options
* Select the correct answer
* Configure basic test settings
* Preview a test
* Create and publish a test
* Receive a unique test code
* Copy or share the test code
* View their created tests
* View test details
* View student attempts and results for their tests
* View relevant proctoring alerts for their tests
* Add review notes
* View basic examination reports
* Manage their profile information

The first version will not include a complex question-bank system or advanced candidate-management system.

### 6.3 Administrator

Administrators can:

* Log in through the admin interface
* View platform-level information
* Manage users
* View user details
* Manage examinations
* View examination details
* View examination attempts
* Access authorized proctoring records
* View flagged examination events
* View basic platform reports
* Manage basic platform settings
* View audit-related activity where implemented
* Manage their profile information

The Admin role will provide platform-level control but will not require a large enterprise administration system in the first version.

---

## 7. Core Examination Scope

The first version of Proxam AI will focus on **single-correct MCQ-based examinations**.

### 7.1 Included Features

The examination system will include:

* Single-correct-answer MCQs
* Four or more answer options, depending on test configuration
* Question display
* Answer selection
* Clear answer
* Mark for review
* Question navigation
* Question palette
* Exam timer
* Automatic answer saving
* Previous and next question controls
* Submit examination option
* Submit confirmation dialog
* Automatic submission when the timer expires
* Basic test instructions
* Test-code-based access
* Automatic MCQ evaluation
* Score calculation
* Result generation
* Examination history
* Basic result summary

### 7.2 Not Included in the First Version

The first version will not include:

* Multiple-correct-answer MCQs
* Descriptive or long-answer questions
* Subjective answer evaluation
* Essay grading
* Handwritten answer recognition
* Voice-answer evaluation
* Coding-question evaluation
* File-upload questions
* Live human video conversation with a proctor
* Advanced adaptive testing
* Complex question-bank categorization
* Complex candidate-group management
* Paid examinations
* Subscription management
* Public examination marketplace
* Native mobile applications

These features may be considered in future versions.

---

## 8. Test Creation and Access Workflow

The main examination workflow will be based on a unique test code.

```text
Teacher Logs In
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
Backend Generates Unique Test Code
      ↓
Success Screen Displays Test Code
      ↓
Teacher Shares Test Code
      ↓
Student Logs In
      ↓
Student Enters Test Code
      ↓
Test Details Are Displayed
      ↓
Pre-Exam System Check
      ↓
Identity / Face-Presence Verification
      ↓
Start Examination
      ↓
Answer MCQs
      ↓
Submit Examination
      ↓
Automatic Evaluation
      ↓
Result Generation
```

The test code will be generated and validated by the backend. The frontend will only display the code and allow users to enter or copy it.

Example test code:

```text
PXAM-7K4Q2
```

The first version will not require a public examination catalogue. Students will access examinations through a valid test code.

---

## 9. AI-Assisted Proctoring Scope

Proxam AI will include basic AI-assisted and browser-based monitoring capabilities.

The system will identify potentially suspicious events. These events will not automatically prove that misconduct occurred.

### 9.1 Webcam Monitoring

The system will request webcam permission before the examination begins.

During the active examination, the webcam feed will be used for selected monitoring functions.

The first version will focus on event detection rather than continuous video recording.

The examination interface will display a small webcam preview or monitoring indicator so that the student can understand that monitoring is active.

### 9.2 Microphone Status Monitoring

The system will monitor whether microphone access is available.

The first version will focus on:

* Microphone permission status
* Microphone connection status
* Microphone disconnection events

The first version will not include:

* Continuous audio recording
* Speech transcription
* Voice recognition
* Speech analysis
* Conversation analysis

### 9.3 Face Presence Detection

The system will attempt to identify whether a face is visible in the webcam frame.

Potential events include:

* Face not detected
* Face temporarily absent
* Face repeatedly absent

Temporary face absence may occur because of lighting, camera position, or movement. Therefore, the system will record the event as a signal requiring context rather than automatically treating it as cheating.

### 9.4 Multiple-Face Detection

The system will attempt to identify when more than one face appears in the webcam frame.

Potential events include:

* Multiple faces detected
* Multiple faces repeatedly detected

These events will be stored for authorized review.

### 9.5 Basic Identity / Face-Presence Verification

Before the examination begins, the student will complete a basic verification step.

The first version will use a simple live face-presence or camera verification process.

The first version will not require:

* Face matching against a registered profile photograph
* Advanced biometric identity verification
* Government identity document verification
* Advanced liveness detection
* Facial recognition databases

The exact implementation may include checking whether the camera is working and whether one visible face is present before allowing the examination to start.

### 9.6 Looking-Away Detection

The system will attempt to identify prolonged or repeated head orientation away from the examination screen.

Potential events include:

* Looking away for an extended period
* Repeated looking-away events

This detection may not always be accurate. It will therefore be treated as a potentially suspicious signal that requires context and human review.

### 9.7 Tab-Switch and Fullscreen Monitoring

The browser session will monitor events such as:

* Leaving the examination tab
* Switching browser tabs
* Switching browser windows
* Exiting fullscreen mode
* Repeated visibility changes
* Attempting to move away from the examination page

These controls will be implemented within the limitations of a browser-based application. A normal website cannot provide the same level of control as a dedicated lockdown browser.

### 9.8 Network Monitoring

The system may monitor basic network connectivity during an active examination.

Potential events include:

* Network disconnected
* Network reconnected
* Temporary connection interruption

Network-related events will be treated as technical events and will not automatically be considered suspicious behavior.

---

## 10. Video and Privacy Policy

Proxam AI will not continuously record or permanently store the student's webcam video in the first version.

Instead, the system will preferably store structured event metadata such as:

* Event type
* Event timestamp
* Attempt ID
* Candidate ID
* Test ID
* Detection confidence, where applicable
* Event description
* Event duration, where applicable
* Review status
* Reviewer notes
* Final review decision, where applicable

The system will request appropriate camera and microphone permissions and clearly communicate the purpose of monitoring to the student.

Access to proctoring data will be restricted to authorized users.

The first version will not include:

* Continuous webcam video storage
* Continuous audio storage
* Permanent screen recording
* Speech recording
* Facial emotion analysis
* Mental-state analysis
* Advanced biometric surveillance

---

## 11. Proctoring Review Workflow

The system will not automatically conclude that a student cheated.

The review workflow will be:

```text
Monitoring Signal
      ↓
Potentially Suspicious Event
      ↓
Event Metadata Recorded
      ↓
Attempt May Be Flagged for Review
      ↓
Authorized Teacher or Admin Reviews Events
      ↓
Reviewer Adds Notes
      ↓
Reviewer Records Review Status or Decision
```

Possible review statuses may include:

* Unreviewed
* Under Review
* Reviewed
* No Concern
* Requires Further Review
* Decision Recorded

The first version will keep the review workflow simple.

Teachers may review proctoring events associated with their own tests. Admins may access platform-level proctoring records and handle escalated cases.

The system will not automatically invalidate an examination based only on an AI-generated event.

---

## 12. Main Platform Modules

Proxam AI will be divided into the following modules.

### 12.1 Authentication Module

* Registration
* Login
* Logout
* Forgot password
* Password reset
* Role-based access
* Session management
* Protected routes

### 12.2 User Profile Module

* View profile
* Edit basic profile information
* Display role-specific information
* Basic account settings

### 12.3 Test Creation Module

* Create test
* Enter test title
* Enter test description
* Configure duration
* Configure total marks
* Add MCQ questions
* Add answer options
* Select correct answer
* Configure basic marking settings
* Preview test
* Create test
* Generate unique test code

### 12.4 Test Management Module

* View created tests
* View test details
* View test code
* Copy test code
* View test status
* View student attempts
* View test results
* View related proctoring alerts

The first version will not include complex test scheduling or candidate-group management.

### 12.5 Test Access Module

* Enter test code
* Validate test code
* Display test details
* Display invalid-code error
* Display unavailable-test error
* Prevent unauthorized access
* Prevent duplicate or invalid attempts where supported

### 12.6 Examination Attempt Module

* Examination instructions
* Pre-exam system check
* Camera permission check
* Microphone status check
* Basic face-presence verification
* Fullscreen request
* Timed examination
* MCQ display
* Answer selection
* Answer saving
* Question navigation
* Mark for review
* Question palette
* Submission confirmation
* Manual submission
* Automatic submission

### 12.7 Evaluation and Results Module

* Automatic MCQ evaluation
* Score calculation
* Correct-answer count
* Incorrect-answer count
* Unanswered-question count
* Percentage calculation
* Result generation
* Result display
* Examination history

### 12.8 AI-Assisted Proctoring Module

* Webcam monitoring
* Microphone status monitoring
* Face presence detection
* Multiple-face detection
* Basic face-presence verification
* Looking-away detection
* Tab-switch monitoring
* Fullscreen monitoring
* Network status monitoring
* Event metadata recording

### 12.9 Review Module

* View flagged attempts
* View proctoring events
* View event timeline
* Filter events
* View event details
* Add reviewer notes
* Update review status
* Record review decision

### 12.10 Admin Module

* Admin dashboard
* User management
* User details
* Test management
* Test details
* Attempt overview
* Proctoring alert overview
* Basic reports
* Basic system settings
* Admin profile

---

## 13. Application Areas

The application will contain the following main areas.

### 13.1 Public and Authentication Area

* Landing page
* Login page
* Registration page
* Forgot password page
* Password reset page, if implemented
* Authentication feedback states

### 13.2 Teacher Area

* Teacher dashboard
* Create test
* Test details
* Test preview
* Test creation success screen
* Test records
* Test attempts and results
* Proctoring alerts related to teacher-created tests
* Teacher profile

### 13.3 Student Area

* Student dashboard
* Enter test code
* Test details
* Pre-exam instructions
* System check
* Identity or face-presence verification
* Examination interface
* Submit confirmation
* Exam submitted screen
* Result page
* Examination history
* Student profile

### 13.4 Admin Area

* Admin dashboard
* User management
* User details
* Test management
* Test details
* Attempt overview
* Proctoring alerts
* Basic reports
* Admin profile
* Basic system settings, if required

---

## 14. Examination Interface Requirements

The active examination interface will be focused and distraction-free.

It should include:

* Test title
* Remaining time
* Current question number
* Question text
* Answer options
* Next button
* Previous button
* Clear answer button
* Mark for review button
* Question palette
* Submit button
* Answer-saving status
* Small webcam preview or monitoring indicator
* Monitoring status
* Important technical warnings

The examination interface should not contain:

* Large decorative illustrations
* Excessive cards
* Unnecessary navigation
* Social features
* Public comments
* Complex dashboards
* Distracting animations

The examination should enter fullscreen mode when supported and requested.

---

## 15. Proctoring Interface Requirements

The proctoring interface should communicate monitoring status without creating unnecessary fear or distraction.

It may include:

* Small webcam preview
* Monitoring active indicator
* Camera status
* Microphone status
* Face detection status
* Network status
* Fullscreen status
* Warning messages
* Technical recovery instructions

Potential warnings include:

* Camera permission required
* Microphone permission required
* Face not detected
* Multiple faces detected
* Please remain visible to the camera
* Fullscreen mode exited
* Browser tab changed
* Network connection interrupted
* Camera disconnected

Warnings should be clear, short, and informative.

The interface should not use aggressive surveillance-style graphics or repeated red alerts for every minor event.

---

## 16. Security and Access Requirements

The first version will include basic security and access controls.

These include:

* Secure authentication
* Role-based authorization
* Protected routes
* Backend validation of test codes
* Backend validation of test ownership
* Backend validation of student attempts
* Secure password hashing
* Session management
* Restricted access to proctoring data
* Restricted access to test results
* Input validation
* Server-side answer evaluation
* Prevention of unauthorized test modification
* Prevention of unauthorized result access

The frontend must not be treated as the final security layer. Important permissions and validations must be implemented on the backend.

---

## 17. Project Boundaries

### 17.1 The Project Will Focus On

* Browser-based online examinations
* Single-correct MCQ tests
* Three primary roles: Student, Teacher, and Admin
* Teacher-created tests
* Unique test-code-based examination access
* Pre-exam system checks
* Basic identity or face-presence verification
* AI-assisted event detection
* Browser-based monitoring
* Human review of potentially suspicious events
* Automatic objective evaluation
* Result generation
* Basic examination history
* Secure role-based access

### 17.2 The Project Will Not Initially Focus On

* Multiple-correct MCQs
* Descriptive questions
* Coding examinations
* Subjective evaluation
* Continuous video recording
* Continuous audio recording
* Fully autonomous cheating detection
* Automatic cheating verdicts
* Facial emotion recognition
* Mental-state analysis
* Speech transcription
* Advanced biometric surveillance
* Government identity verification
* Advanced liveness detection
* Dedicated lockdown browser development
* Public examination marketplace
* Paid examinations
* Subscription management
* Complex question-bank management
* Complex candidate-group management
* Large-scale enterprise analytics
* Native mobile applications
* Large-scale commercial deployment

---

## 18. Expected Outcome

The expected outcome is a functional web-based examination platform where:

* Students can register and log in
* Teachers can create MCQ-based tests
* The system can generate unique test codes
* Students can enter a valid test code
* Students can complete pre-exam checks
* Students can attempt timed examinations
* The system can monitor selected webcam, microphone, and browser signals
* Potentially suspicious events can be recorded as metadata
* Authorized teachers and admins can review relevant events
* MCQ answers can be evaluated automatically
* Results can be generated and displayed
* Students can view their examination history
* Admins can manage users and examinations

The final project should demonstrate the integration of:

* Modern frontend development
* Backend API development
* Authentication and authorization
* Database management
* MCQ examination workflows
* Browser APIs
* AI-assisted computer vision
* Event-based monitoring
* Automatic evaluation
* Human review processes
* Secure data access

---

## 19. Finalized Product Decisions

The following decisions are confirmed for the first version:

1. The product name is **Proxam AI**.
2. The platform will support exactly three roles:

   * Student
   * Teacher / Examination Creator
   * Admin
3. The examination format will be MCQ-only.
4. The first version will support single-correct MCQs.
5. Students will access tests using a unique test code.
6. Teachers will create tests directly through the Create Test workflow.
7. The first version will not contain a public examination catalogue.
8. The first version will not contain a complex question-bank system.
9. Identity verification will initially use a simple live face-presence or camera verification step.
10. The first version will not require face matching against a registered profile photo.
11. Webcam video will not be continuously recorded or permanently stored.
12. Proctoring will record structured event metadata.
13. Proctoring events will not automatically prove cheating.
14. Teachers may review events associated with their own tests.
15. Admins will have platform-level access to authorized proctoring records.
16. The examination interface will use fullscreen mode where supported.
17. A small webcam preview or monitoring indicator will remain visible during the examination.
18. The first version will focus on a functional and achievable scope rather than enterprise-level complexity.

---

## 20. Completion Criteria

The project will be considered functionally complete when:

* A user can register and log in
* The system correctly identifies the user's role
* A teacher can create a test
* A teacher can add single-correct MCQ questions
* The system generates a unique test code
* A student can enter the test code
* The system validates the test code
* The student can complete the pre-exam checks
* The student can start and attempt the examination
* Answers are saved correctly
* The timer works correctly
* The student can submit the examination
* The system automatically evaluates the answers
* The result is generated
* The student can view the result
* The student can view examination history
* Proctoring events can be detected and stored
* Authorized users can review relevant proctoring events
* Admins can manage basic users and tests
* Unauthorized users cannot access protected data
* The main workflows work on desktop and responsive layouts
* The application provides clear error, loading, empty, and success states
