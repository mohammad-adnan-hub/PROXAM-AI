# Proxam AI — Design System and UI Guidelines

## 1. Design Overview

Proxam AI is an online examination platform with AI-assisted proctoring for students, teachers, and administrators.

The interface should follow a **modern pastel education SaaS theme** inspired by the provided visual reference.

The design should feel:

* Calm
* Friendly
* Modern
* Premium
* Spacious
* Trustworthy
* Educational
* Easy to understand

The interface should not look like a cybersecurity monitoring system, hospital dashboard, or aggressive surveillance platform.

The product functionality remains serious, but the visual design should communicate confidence without creating unnecessary anxiety.

---

## 2. Design Direction

### Primary Design Style

> Pastel educational dashboard + modern SaaS interface + focused examination experience

The design should use:

* Warm off-white backgrounds
* Soft pastel colors
* Large rounded corners
* Spacious layouts
* Dark charcoal typography
* Minimal line icons
* Soft shadows
* Rounded pill-shaped buttons
* Clean dashboard cards
* Simple navigation
* Clear information hierarchy

### Visual References

The visual language should be inspired by products and interfaces that use:

* Editorial-style large headings
* Soft pastel cards
* Rounded navigation controls
* Minimal black icons
* White content surfaces
* Spacious dashboard composition
* Calm and friendly visual hierarchy

The uploaded reference image should be treated as the primary visual reference for:

* Color mood
* Card shapes
* Navigation style
* Spacing
* Typography
* Dashboard composition
* Profile panel
* Button shapes
* Overall visual atmosphere

---

## 3. Core Design Principles

### 3.1 Calm, Not Clinical

The interface should look approachable and human.

Avoid:

* Hospital-like layouts
* Medical blue color schemes
* Excessive warning banners
* Aggressive surveillance visuals
* Red-heavy interfaces

### 3.2 Simple, Not Empty

The design should be spacious but still provide useful information.

Every screen should have:

* A clear heading
* A short supporting description where needed
* One primary action
* Clearly grouped content
* Helpful empty states

### 3.3 Functional, Not Decorative

Pastel colors and rounded cards should support information hierarchy.

Do not use decorative elements that:

* Distract from examination tasks
* Reduce readability
* Make forms harder to complete
* Hide important information
* Create unnecessary visual noise

### 3.4 Trust Through Transparency

Proctoring-related information should be explained clearly.

The interface should communicate:

* What is being checked
* Why camera and microphone access is required
* What happens if a problem occurs
* That proctoring events may be reviewed
* That the system does not automatically declare a student guilty of cheating

### 3.5 Consistent Across Roles

Student, Teacher, and Admin interfaces should share:

* The same typography
* The same color tokens
* The same button styles
* The same spacing system
* The same card radius
* The same status labels
* The same interaction patterns

Only the content and available actions should change by role.

---

## 4. Color System

The interface should use a warm, pastel-based color palette.

### 4.1 Base Colors

```css
:root {
  --color-background: #F8F6F2;
  --color-surface: #FFFFFF;
  --color-surface-soft: #F1EEE8;

  --color-text-primary: #111111;
  --color-text-secondary: #686868;
  --color-text-muted: #969696;

  --color-border: #E8E4DD;
  --color-border-strong: #D8D2C9;

  --color-primary: #111111;
  --color-primary-hover: #292929;

  --color-mint: #B9EAD8;
  --color-mint-strong: #8FD5BD;

  --color-lavender: #D5D0FF;
  --color-peach: #F8D9B5;
  --color-pink: #F4B9C2;
  --color-blue: #C8E2F5;
  --color-yellow: #F4E6A8;

  --color-success: #9BD9BD;
  --color-warning: #F3C58E;
  --color-danger: #E9A4A4;
  --color-info: #BFDDF2;
}
```

### 4.2 Color Usage

| Color          | Usage                                                      |
| -------------- | ---------------------------------------------------------- |
| Warm off-white | Main application background                                |
| White          | Main content cards and forms                               |
| Black          | Primary buttons, headings, active icons                    |
| Mint           | Success, active states, positive information               |
| Lavender       | Secondary cards, navigation highlights, information groups |
| Peach          | Warnings, attention states, timers                         |
| Pink           | Decorative card variation, selected records                |
| Pale blue      | Informational messages and neutral highlights              |
| Soft yellow    | Pending states and reminders                               |
| Muted coral    | Errors and serious interruptions                           |

### 4.3 Color Rules

* Do not use all pastel colors on the same screen without hierarchy.
* Use one dominant pastel accent and one supporting accent per screen.
* Use black or dark charcoal for primary actions.
* Use red only for actual errors or serious interruptions.
* Do not use neon colors.
* Do not use generic blue-purple gradients.
* Do not use strong glowing effects.
* Do not use gradients as the primary visual style.

---

## 5. Theme Modes

Proxam AI should support both:

* Light theme
* Dark theme

The light theme is the primary visual reference and should be implemented first.

### 5.1 Light Theme

The light theme should use:

* Warm ivory background
* White content surfaces
* Dark charcoal text
* Pastel accent cards
* Soft borders
* Minimal shadows

### 5.2 Dark Theme

The dark theme should preserve the same design language rather than becoming a neon technical interface.

```css
[data-theme="dark"] {
  --color-background: #171716;
  --color-surface: #222220;
  --color-surface-soft: #2B2A27;

  --color-text-primary: #F5F2EC;
  --color-text-secondary: #B9B5AE;
  --color-text-muted: #85817A;

  --color-border: #3A3833;
  --color-border-strong: #4A4740;

  --color-primary: #F5F2EC;
  --color-primary-hover: #FFFFFF;
}
```

Pastel colors may be slightly darkened or desaturated in dark mode to maintain readability.

---

## 6. Typography

### 6.1 Font Family

Recommended font combination:

* Primary font: `Inter`
* Display font: `Manrope`
* Test code font: `JetBrains Mono`

```css
body {
  font-family: "Inter", sans-serif;
}

h1,
h2,
h3,
h4 {
  font-family: "Manrope", sans-serif;
}
```

### 6.2 Typography Hierarchy

| Element         | Style                             |
| --------------- | --------------------------------- |
| Page heading    | Large, bold, tight letter spacing |
| Section heading | Medium-large, semibold            |
| Card title      | Semibold, readable                |
| Body text       | Regular, comfortable line height  |
| Metadata        | Small, muted                      |
| Button text     | Medium or semibold                |
| Test code       | Monospace, high contrast          |
| Status label    | Small, medium weight              |

### 6.3 Typography Rules

* Use large headings for major dashboard pages.
* Keep headings short.
* Avoid excessive uppercase text.
* Use sentence case for labels.
* Use comfortable line spacing.
* Do not use too many font weights.
* Use dark charcoal instead of pure black where appropriate.

Example heading style:

```css
.page-title {
  font-family: "Manrope", sans-serif;
  font-size: clamp(2rem, 4vw, 4rem);
  font-weight: 700;
  line-height: 1.05;
  letter-spacing: -0.05em;
}
```

---

## 7. Layout System

### 7.1 Application Layout

The main application layout should use:

```text
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Navigation Rail │ Main Content Area │ Optional Side Panel  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 7.2 Desktop Layout

On desktop:

* Soft vertical navigation rail on the left
* Main content area in the center
* Optional profile/activity panel on the right
* Large horizontal spacing
* Rounded content surfaces

### 7.3 Tablet Layout

On tablet:

* Collapsed navigation rail
* Main content area
* Optional side panel converted into a drawer
* Two-column cards where space allows

### 7.4 Mobile Layout

On mobile:

* Compact top navigation or bottom navigation
* Single-column content
* Full-width buttons
* Side panels converted into drawers
* Tables converted into stacked cards
* Forms displayed in one column

### 7.5 Examination Layout

The active examination should prioritize focus and readability.

It should use:

* Fullscreen layout
* Fixed top examination bar
* Main question area
* Question navigation area
* Small floating monitoring preview
* Minimal distractions

The active examination is primarily designed for desktop and laptop screens.

---

## 8. Spacing System

Use a consistent spacing scale.

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
}
```

### Spacing Guidelines

* Page padding: 32–64px on desktop
* Card padding: 24–32px
* Form field spacing: 16–20px
* Section spacing: 32–48px
* Button height: 44–52px
* Input height: 48–56px
* Navigation item height: 44–52px

The interface should feel spacious without wasting excessive screen space.

---

## 9. Border Radius and Shadows

### 9.1 Border Radius

```css
:root {
  --radius-small: 10px;
  --radius-medium: 16px;
  --radius-large: 24px;
  --radius-xl: 32px;
  --radius-pill: 999px;
}
```

### Usage

| Element             | Radius          |
| ------------------- | --------------- |
| Inputs              | 12–16px         |
| Buttons             | Pill or 14–16px |
| Cards               | 20–28px         |
| Main panels         | 24–32px         |
| Avatars             | 50%             |
| Status labels       | Pill            |
| Test code container | 20–24px         |

### 9.2 Shadows

Use subtle shadows only.

```css
.card-shadow {
  box-shadow: 0 8px 30px rgba(20, 20, 20, 0.04);
}
```

Avoid:

* Heavy shadows
* Multiple layered shadows
* Neon glow
* Strong floating effects
* Excessive glassmorphism

---

## 10. Navigation Design

The navigation should resemble a soft, minimal vertical navigation rail.

### 10.1 Navigation Rail

The navigation rail should include:

* Proxam AI logo
* Role-specific navigation items
* Active navigation state
* Optional notification indicator
* Profile avatar at the bottom
* Help or support access

The rail should use:

* Warm cream or white background
* Rounded navigation items
* Simple black line icons
* Minimal labels
* Soft active-state background

### 10.2 Student Navigation

```text
Proxam AI Logo

Dashboard
Enter Test Code
My Records
Results
Help

Profile Avatar
```

### 10.3 Teacher Navigation

```text
Proxam AI Logo

Dashboard
My Tests
Create Test
Attempts and Results
Help

Profile Avatar
```

### 10.4 Admin Navigation

```text
Proxam AI Logo

Overview
Users
Tests
Proctoring Alerts
Help

Profile Avatar
```

### 10.5 Navigation Rules

* Do not create a public examination marketplace.
* Do not include a student examination catalogue.
* Do not include a separate Question Bank navigation item in version one.
* Do not include complex enterprise navigation unless the feature is implemented.
* Use contextual pages for test details, attempts, and reports.
* Keep the number of primary navigation items limited.

---

## 11. Logo and Branding

### Brand Name

**Proxam AI**

The logo should be simple and recognizable at small sizes.

Possible direction:

* Abstract “P” mark
* Minimal geometric examination symbol
* Simple document/checkmark combination
* Clean wordmark

Avoid:

* Robot illustrations
* Brain icons
* Excessive AI imagery
* Neon circuits
* Complicated shield graphics
* Overly technical cybersecurity symbols

### Brand Usage

The brand should appear in:

* Navigation rail
* Authentication pages
* Examination header
* Success screens
* Error pages
* Footer where required

---

## 12. Buttons

### 12.1 Primary Button

Primary actions should use a dark charcoal or black pill-shaped button.

Examples:

* Create Test
* Enter Test Code
* Start Examination
* Submit Examination
* Save Test

```css
.button-primary {
  background: #111111;
  color: #FFFFFF;
  border-radius: 999px;
  padding: 14px 22px;
  font-weight: 600;
}
```

### 12.2 Secondary Button

Secondary actions should use:

* White background
* Soft border
* Dark text
* Rounded shape

Examples:

* View Details
* Preview Test
* Cancel
* Back

### 12.3 Pastel Button

Pastel buttons may be used for lower-priority actions.

Examples:

* View Records
* Copy Code
* Share Code
* Continue

### 12.4 Button Rules

* Every screen should have one clear primary action.
* Avoid multiple equally prominent buttons.
* Use icons only when they improve recognition.
* Buttons must have visible hover, focus, disabled, and loading states.
* Destructive actions should not use the primary black style without confirmation.

---

## 13. Form Design

Forms should be clean, spacious, and easy to complete.

### 13.1 Input Style

Inputs should use:

* White or soft cream background
* Thin warm-gray border
* Rounded corners
* Comfortable height
* Clear labels
* Visible focus state

```css
.input {
  min-height: 52px;
  padding: 0 16px;
  border: 1px solid #E8E4DD;
  border-radius: 14px;
  background: #FFFFFF;
  color: #111111;
}
```

### 13.2 Form Rules

* Every input must have a visible label.
* Placeholder text should not replace labels.
* Required fields must be clearly identified.
* Validation messages should appear close to the relevant field.
* Do not use red borders before the user interacts with a field.
* Preserve entered values when validation fails.
* Use clear helper text for technical requirements.

### 13.3 Test Creation Form

The teacher test creation form should include:

* Test title
* Description
* Duration
* Instructions
* Optional subject or category
* MCQ question entries
* Correct answer selection
* Preview action

Avoid unnecessary first-version fields such as:

* Complex scheduling rules
* Candidate assignment
* Negative marking configuration
* Advanced randomization
* Multiple question types
* Question bank selection

These may be added later if required.

---

## 14. Card Design

Cards are a major part of the visual identity.

### 14.1 Card Style

Cards should use:

* White or pastel background
* 20–28px radius
* Comfortable padding
* Minimal shadow
* Clear title
* Supporting metadata
* One or two actions

### 14.2 Pastel Card Usage

Pastel cards may represent:

* Test records
* Statistics
* Recent activity
* Success states
* Informational sections
* Profile summaries

Do not assign random colors without meaning. Use colors consistently where possible.

### 14.3 Test Record Card

A test record card may contain:

* Test title
* Test code
* Duration
* Number of questions
* Status
* Date
* Attempt count
* View details action

Example:

```text
┌─────────────────────────────────────┐
│ Mathematics Assessment       Mint   │
│ PXAM-7K4Q2                          │
│ 20 Questions · 30 Minutes           │
│ Created 18 September 2026            │
│                                     │
│ [View Details]                      │
└─────────────────────────────────────┘
```

---

## 15. Student Dashboard Design

The student dashboard should follow the reference image’s spacious educational dashboard composition.

### Main Content

The dashboard should contain:

* Welcome heading
* Brief student information
* Prominent Enter Test Code action
* Recent examination records
* Completed examination cards
* Latest result summary
* Optional activity summary

### Suggested Heading

> Continue your examination journey

### Primary Action

```text
[ Enter Test Code → ]
```

### Dashboard Rules

* Enter Test Code must be the most visible action.
* Do not show a public examination marketplace.
* Do not assume that students have a catalogue of assigned exams.
* Show records based on actual student activity.
* Use empty states when the student has no examination history.
* Keep statistics simple and useful.

---

## 16. Teacher Dashboard Design

The teacher dashboard should follow the same pastel card layout.

### Main Content

The dashboard should contain:

* Brief teacher information
* Prominent Create Test action
* Total tests created
* Total attempts
* Recent test records
* Test status summaries
* Quick access to test details

### Suggested Heading

> Manage your examinations

### Primary Action

```text
[ Create Test → ]
```

### Test Cards

Each card may display:

* Test title
* Test code
* Number of questions
* Duration
* Status
* Number of attempts
* Created date

The teacher should be able to open a test card to access:

* Test details
* Questions
* Attempts
* Results
* Proctoring events associated with attempts

---

## 17. Create Test Design

The test creation flow should be simple and sequential.

```text
Test Details
    ↓
Add MCQ Questions
    ↓
Preview Test
    ↓
Create Test
    ↓
Test Created Successfully
```

### 17.1 Test Details Screen

The screen should include:

* Page heading
* Short description
* Test title field
* Description field
* Duration field
* Instructions field
* Continue button

### 17.2 Add MCQ Questions Screen

Each question should be displayed in a separate rounded card.

```text
Question 01

[ Enter question text ]

A. [ Option text ]
B. [ Option text ]
C. [ Option text ]
D. [ Option text ]

Correct answer: [ Select option ]

[ Remove Question ]
```

Features:

* Add question
* Remove question
* Edit question
* Select correct answer
* Save progress locally or through the backend
* Continue to preview

### 17.3 Preview Screen

The preview should show:

* Test title
* Instructions
* Duration
* Question count
* All questions
* Answer options
* Correct-answer information visible only to the teacher
* Edit test button
* Create test button

### 17.4 Creation Success Screen

After successful creation, display:

```text
Your test is ready

PXAM-7K4Q2

[ Copy Code ] [ Share Code ]

Students can use this code to enter the examination.

[ View Test ] [ Return to Dashboard ]
```

The generated code should be visually prominent.

---

## 18. Test Code Component

The test code is central to the application flow.

### Design Requirements

The code should:

* Be easy to read
* Use a monospace font
* Have high contrast
* Be visually separated from surrounding text
* Support copying
* Show a copy-success state
* Be displayed on test details and creation success screens

### Example

```css
.test-code {
  font-family: "JetBrains Mono", monospace;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  background: #B9EAD8;
  color: #111111;
  border-radius: 20px;
  padding: 20px 24px;
}
```

---

## 19. Enter Test Code Design

The student’s Enter Test Code screen should be simple and focused.

### Layout

```text
Enter your examination code

Use the unique code provided by your teacher.

[ PXAM-______ ]

[ Continue → ]
```

### Behavior

* Accept the generated test code
* Normalize unnecessary spaces or lowercase input where appropriate
* Validate the code through the backend
* Show a clear error for invalid or expired codes
* Open test details for a valid code

### Error Examples

* Test code not found
* Test is no longer available
* Test has expired
* You have already submitted this examination
* Unable to connect to the server

---

## 20. Test Details Design

The test details screen should show the student what they are about to attempt.

### Information

* Test title
* Teacher name or identifier
* Description
* Number of questions
* Duration
* Instructions
* Proctoring requirements
* Start examination button

### Proctoring Notice

The screen should clearly explain:

* Camera access is required
* Microphone status may be checked
* Face presence may be monitored
* Fullscreen mode is required during the examination
* Proctoring events may be recorded as metadata for review
* Continuous video or audio recording is not part of the first version

The notice should be informative rather than intimidating.

---

## 21. Pre-Exam System Check Design

The system-check screen should use a clean two-column layout on desktop.

### Left Side

* Camera preview
* Camera status
* Microphone status
* Face presence status
* Browser compatibility status
* Fullscreen readiness
* Network status

### Right Side

* Examination instructions
* Required permissions
* Troubleshooting guidance
* Continue button

### Example Statuses

```text
Camera                 Ready
Microphone             Ready
Face visibility        Detected
Browser                 Supported
Network                 Connected
Fullscreen              Ready
```

Use mint for ready states and soft peach for issues.

### Important Rule

Camera and microphone permissions should be requested before entering the active examination.

Fullscreen should be activated when the examination begins, subject to browser permissions and limitations.

---

## 22. Identity and Face-Presence Verification

The identity verification interface should remain basic and non-invasive.

It may include:

* Camera preview
* Face-position guidance
* Basic face presence check
* Verification progress
* Retry action
* Clear failure message

Avoid presenting:

* Facial-recognition confidence scores
* Biometric percentages
* Automatic guilt or cheating labels
* Invasive identity claims
* Unexplained AI decisions

The exact verification method may depend on the technical implementation.

---

## 23. Active Examination Design

The active examination interface should be visually calmer than the dashboard.

### Main Structure

```text
┌─────────────────────────────────────────────────────────────┐
│ Proxam AI │ Test Title │ Question Count │ Timer │ Monitoring │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Question 04 of 20                                           │
│                                                             │
│ Question text                                               │
│                                                             │
│ ○ Option A                                                  │
│ ○ Option B                                                  │
│ ○ Option C                                                  │
│ ○ Option D                                                  │
│                                                             │
│ [Previous] [Mark for Review] [Next]                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Question Navigator                         Webcam Preview   │
└─────────────────────────────────────────────────────────────┘
```

### 23.1 Question Panel

The question panel should use:

* White surface
* Large readable question text
* Clear answer options
* Generous spacing
* Rounded answer containers
* Visible selected state

### 23.2 Answer Option Style

Unselected:

* White background
* Light border
* Dark text

Selected:

* Soft mint background
* Dark border or stronger contrast
* Clear selection indicator

### 23.3 Navigation

The examination may include:

* Previous button
* Next button
* Question number
* Question navigator
* Mark for Review option
* Submit button

Mark for Review should only be implemented if included in the final functionality.

### 23.4 Timer

The timer should be visible but not visually aggressive.

Normal state:

* Neutral dark text

Low-time state:

* Soft peach background

Critical state:

* Muted coral background

Avoid flashing or excessively animated timers.

---

## 24. Proctoring Monitoring UI

The proctoring interface should be small, clear, and non-obstructive.

### 24.1 Floating Monitoring Preview

A small floating webcam preview should remain visible during the examination.

It should include:

* Webcam video preview
* Monitoring status
* Camera connection state
* Optional minimize control if allowed
* No large surveillance-style panel

Example:

```text
┌─────────────────────────┐
│ Webcam Preview          │
│                         │
│       Student View      │
│                         │
│ ● Monitoring Active     │
└─────────────────────────┘
```

### 24.2 Monitoring Status

Normal state:

> Monitoring Active

Camera disconnected:

> Camera connection interrupted

Face not detected:

> Please remain visible in the camera frame

Multiple faces:

> Multiple faces detected. Ensure only the examinee is visible.

Fullscreen exited:

> Return to fullscreen to continue.

Microphone issue:

> Microphone status could not be verified.

Network issue:

> Connection interrupted. Your session is being checked.

### 24.3 Proctoring Rules

Do not display:

* “Cheating detected”
* “Fraud probability”
* “Suspicious candidate”
* “AI verdict”
* “Guilty”
* Unexplained confidence scores

The system should record structured proctoring events and allow appropriate human review.

---

## 25. Submission and Result Design

### 25.1 Submission Confirmation

Use a modal or in-page confirmation.

```text
Submit examination?

You will not be able to change your answers after submission.

[Cancel] [Submit Examination]
```

### 25.2 Exam Submitted Screen

The submitted screen should communicate completion clearly.

```text
Your examination has been submitted

Your responses were recorded successfully.

[ View Result ] [ Return to Dashboard ]
```

Use a mint success panel and a simple completion icon.

### 25.3 Result Screen

The result screen may show:

* Test title
* Score
* Total questions
* Correct answers
* Incorrect answers
* Unanswered questions
* Percentage
* Submission time
* Basic performance summary

Do not use overly complex analytics in version one.

### 25.4 Student Records

Records should be shown as:

* Clean cards on dashboards
* Simple table on desktop
* Stacked cards on mobile

Each record may show:

* Test title
* Date
* Score
* Status
* View result action

---

## 26. Teacher Attempts and Results Design

The teacher should be able to view attempts for a specific test.

### Information

* Student name or identifier
* Submission status
* Score
* Start time
* Submission time
* Proctoring event count
* View attempt action

### Attempt Review

The attempt review screen may show:

* Student information
* Test information
* Answers
* Score
* Proctoring event timeline
* Event type
* Event timestamp
* Event description

Use neutral event labels such as:

* Face not detected
* Multiple faces detected
* Fullscreen exited
* Tab visibility changed
* Camera disconnected
* Network interrupted

Do not automatically label an attempt as cheating.

---

## 27. Admin Design

The Admin interface should remain simple and functional.

### Admin Dashboard

Show:

* Total users
* Total tests
* Total attempts
* Recent activity
* Recent proctoring alerts
* Basic system status

### User Management

Use a clean table with:

* Name
* Email
* Role
* Account status
* Created date
* View details action

### Test Management

Use a clean table or card layout with:

* Test title
* Creator
* Test code
* Status
* Number of attempts
* Created date
* View details action

### Proctoring Alerts

Show:

* Event type
* Student
* Test
* Timestamp
* Event status
* Review action

Avoid building a complex live monitoring wall in version one.

### Admin Navigation

The following should remain optional unless implemented:

* Advanced audit logs
* Complex system settings
* Permission editor
* Enterprise analytics
* Advanced activity center

---

## 28. Status Labels

Status labels should use short, readable text.

### Examination Statuses

* Draft
* Available
* Active
* Completed
* Closed
* Archived

### Attempt Statuses

* Not Started
* In Progress
* Submitted
* Expired
* Abandoned
* Under Review

### Account Statuses

* Active
* Pending
* Suspended
* Inactive

### Status Styling

Use pastel backgrounds:

* Mint: active, completed, successful
* Lavender: neutral information
* Peach: pending, attention required
* Pale blue: informational
* Muted coral: error, suspended, failed

---

## 29. Alerts, Modals, and Notifications

### 29.1 Alerts

Alerts should be:

* Short
* Specific
* Actionable
* Calm
* Close to the relevant content

### 29.2 Modal Rules

Use modals for:

* Submission confirmation
* Delete confirmation
* Session expiry
* Permission instructions
* Important examination interruptions

Do not use modals for every small action.

### 29.3 Toast Notifications

Use toasts for:

* Test code copied
* Test saved
* Profile updated
* Question added
* Changes discarded
* Network reconnected

---

## 30. Empty States

Empty states should be helpful rather than decorative.

### Student Without Records

```text
No examination records yet

Enter a test code provided by your teacher to begin.

[ Enter Test Code ]
```

### Teacher Without Tests

```text
You have not created any tests yet

Create your first examination and share its code with students.

[ Create Test ]
```

### No Attempts

```text
No attempts yet

Student submissions will appear here after they begin the examination.
```

### No Proctoring Alerts

```text
No proctoring alerts

No reviewable events are available for this test.
```

---

## 31. Loading and Error States

### Loading

Use:

* Skeleton cards
* Soft shimmer only where useful
* Button loading indicators
* Clear loading text for important actions

Avoid excessive animation.

### Error

Error states should include:

* What went wrong
* Whether the user can retry
* A clear next action

Example:

```text
Something went wrong

We could not load this test. Please try again.

[ Try Again ]
```

### Network Interruption

During an examination:

* Show a calm connection warning
* Preserve local answer state where possible
* Attempt reconnection
* Clearly communicate whether the examination can continue

---

## 32. Accessibility

The interface should follow accessible design practices.

### Requirements

* Use semantic HTML
* Maintain sufficient color contrast
* Do not rely only on color to communicate status
* Provide visible keyboard focus states
* Support keyboard navigation
* Use descriptive labels
* Associate form errors with inputs
* Provide accessible button names
* Use readable font sizes
* Avoid very small text
* Respect reduced-motion preferences

### Focus Ring

```css
:focus-visible {
  outline: 3px solid #8FD5BD;
  outline-offset: 3px;
}
```

### Color Accessibility

Every status should include:

* Color
* Text label
* Optional icon

For example, do not use only a green dot to indicate success.

---

## 33. Responsive Rules

### Dashboard Screens

Dashboards should be responsive across:

* Desktop
* Tablet
* Mobile

### Forms

Forms should:

* Become single-column on smaller screens
* Use full-width inputs
* Keep actions accessible
* Avoid horizontal scrolling

### Tables

Tables should:

* Become horizontally scrollable only when necessary
* Prefer stacked cards on mobile
* Keep important information visible

### Active Examination

The active examination should primarily support desktop and laptop screens.

If the viewport is too small, show a clear message explaining that a larger supported screen is required for a reliable examination experience.

---

## 34. Motion and Interaction

Animations should be subtle and purposeful.

Use motion for:

* Page transitions
* Button feedback
* Modal appearance
* Toast notifications
* Card hover states
* Progress changes

Avoid:

* Constant floating animations
* Excessive bouncing
* Flashing warnings
* Distracting gradients
* Heavy parallax
* Long transitions

Recommended transition:

```css
transition:
  background-color 180ms ease,
  border-color 180ms ease,
  color 180ms ease,
  transform 180ms ease,
  box-shadow 180ms ease;
```

---

## 35. Privacy and Proctoring Transparency

Before the examination begins, students should see a concise explanation of proctoring.

The explanation should state that the platform may check:

* Camera availability
* Microphone status
* Face presence
* Multiple-face presence
* Fullscreen state
* Tab or visibility changes
* Network connectivity

The first version should not claim to:

* Continuously record video
* Continuously record audio
* Automatically determine cheating
* Provide perfect identity verification
* Guarantee detection of every suspicious behavior

The interface should use accurate, understandable language.

---

## 36. Screens That Must Follow This Design System

### Public and Authentication

* Landing Page
* Login
* Registration
* Forgot Password
* Reset Password
* About
* Help

### Student

* Student Dashboard
* Enter Test Code
* Test Details
* Pre-Exam System Check
* Identity/Face-Presence Verification
* Active Examination
* Submission Confirmation
* Exam Submitted
* Result
* Records/History
* Student Profile

### Teacher

* Teacher Dashboard
* Test Records
* Create Test — Test Details
* Create Test — Add MCQs
* Test Preview
* Test Creation Success
* Test Details
* Attempts and Results
* Attempt/Proctoring Review
* Teacher Profile

### Admin

* Admin Dashboard
* User Management
* User Details
* Test Management
* Test Details
* Proctoring Alerts
* Admin Profile

### Shared

* Not Found
* Unauthorized
* Global Error
* Loading States
* Empty States
* Confirmation Modals
* Toast Notifications

---

## 37. Features Not Represented in the First-Version Design

The following should not be included unless they are deliberately added to the scope:

* Public examination marketplace
* Public exam catalogue
* Complex question bank
* Candidate assignment system
* Advanced scheduling
* Multiple question types
* Descriptive questions
* Coding questions
* Continuous video recording
* Continuous audio recording
* Advanced biometric liveness detection
* Automatic cheating verdicts
* Complex live monitoring wall
* Enterprise-level analytics
* Advanced audit-log interface
* Complex permission editor
* Native mobile application
* Subscription or payment screens

---

## 38. Final Visual Rules

The entire Proxam AI interface should follow these rules:

1. Use a warm off-white background as the primary canvas.
2. Use white surfaces and soft pastel cards.
3. Use large rounded corners.
4. Use dark charcoal typography.
5. Use pill-shaped primary buttons.
6. Use minimal black line icons.
7. Keep layouts spacious.
8. Use pastel colors to organize information, not as decoration only.
9. Keep proctoring indicators calm and understandable.
10. Avoid neon colors and blue-purple gradients.
11. Avoid excessive glassmorphism.
12. Avoid excessive cards on every screen.
13. Avoid dashboard layouts that hide the main task.
14. Keep the active examination focused and distraction-free.
15. Make Enter Test Code highly visible for students.
16. Make Create Test highly visible for teachers.
17. Make the generated test code visually prominent.
18. Use contextual pages instead of unnecessary navigation items.
19. Do not show automatic cheating judgments.
20. Maintain accessibility and responsive behavior throughout the application.

---

## 39. Final Design Statement

Proxam AI should look like a **calm, pastel, modern education platform** with a focused examination experience.

The visual identity should combine:

* The soft pastel dashboard style of the reference image
* The clarity of a modern SaaS product
* The reliability expected from an examination platform
* The transparency required for AI-assisted proctoring

The final interface should feel:

> **Friendly enough for students, practical for teachers, clear for administrators, and trustworthy during examinations.**
