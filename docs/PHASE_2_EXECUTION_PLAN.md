# Proxam AI — Phase 2 Execution Plan

## 1. Objective

Build the Teacher Examination Creation Module using the existing React frontend and FastAPI backend.

The existing authentication system is working and must be preserved.

## 2. Current Working Features

- React + Vite frontend
- FastAPI backend
- Database models and configuration
- Student, Teacher and Admin authentication
- JWT authentication using HTTP-only cookies
- Registration, login and logout
- Session restoration
- Password reset and password change
- Role-based access control
- Protected frontend routes
- Basic landing, authentication and dashboard pages

## 3. Development Rules

1. Inspect existing code before making changes.
2. Reuse existing database models and components wherever possible.
3. Do not rebuild authentication.
4. Do not introduce mock data as a replacement for backend functionality.
5. Follow the existing design system in docs/DESIGN.md.
6. Preserve the existing project architecture.
7. Use Alembic migrations when database changes are required.
8. Never drop or recreate the existing database.
9. Test every milestone before proceeding.
10. Provide a list of modified and created files after each milestone.

## 4. Milestone 1 — Project Inspection

- Read all project documentation.
- Inspect backend models and relationships.
- Inspect existing API routes and authentication.
- Inspect frontend routes and reusable components.
- Review relevant Stitch UI references.
- Prepare an implementation plan.
- Do not modify any files during inspection.

## 5. Milestone 2 — Backend Examination APIs

Implement teacher-protected APIs to:

- Create an examination.
- List examinations belonging to the logged-in teacher.
- Retrieve examination details.
- Update an examination.
- Delete an examination.
- Add, edit, delete and reorder MCQ questions.
- Add four options per question.
- Store exactly one correct answer per question.
- Generate a unique examination code on the server.
- Publish and activate an examination.

Security requirements:

- Only teachers can access teacher examination APIs.
- Teacher ownership must come from the authenticated session.
- Teachers must not access another teacher's examinations.
- Students must never receive correct answers through student-facing APIs.
- Validate all inputs on the backend.
- Save examination and question data safely using database transactions.

## 6. Milestone 3 — Frontend Examination Creation

Build:

### Teacher Dashboard
- Welcome and profile section.
- Total examination count from real backend data.
- Recent examinations.
- Create examination action.
- Examination management section.

### Examination Creation Wizard

Step A — Basic Information:
- Examination title.
- Description.
- Instructions.
- Duration.

Step B — Questions:
- MCQ question text.
- Four options (A, B, C, D).
- Exactly one correct answer.
- Marks per question.
- Add, edit, delete and reorder questions.

Step C — Preview:
- Preview the complete examination.
- Return to previous steps for editing.

Step D — Publish:
- Validate all examination data.
- Publish the examination.
- Display the unique examination code.
- Provide a copy-code action.

Reuse existing frontend components and design tokens.

## 7. Milestone 4 — Integration and Testing

Verify:

- Teacher can create an examination.
- Examination data persists after refresh.
- Questions and options are saved correctly.
- Unique examination code is generated.
- Published examinations appear in the teacher dashboard.
- Teacher ownership is enforced.
- Students cannot access teacher-only APIs.
- Invalid inputs are rejected.
- Existing authentication continues working.
- Frontend production build succeeds.
- Backend tests pass.

## 8. Explicitly Out of Scope for Phase 2

Do not implement these features yet:

- Student examination-taking interface.
- Timed exam execution.
- Webcam monitoring.
- Microphone monitoring.
- AI face detection.
- Continuous video or audio recording.
- Cheating probability or integrity scores.
- Automatic cheating verdicts.

These belong to later development phases.

## 9. Completion Criteria

Phase 2 is complete when a teacher can:

1. Log in.
2. Open the teacher dashboard.
3. Create an examination containing multiple MCQs.
4. Preview the examination.
5. Publish it.
6. Receive a unique examination code.
7. See and manage the published examination from the dashboard.