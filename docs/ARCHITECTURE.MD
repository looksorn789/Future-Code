# Architecture

InterviewPrepAI is a cloud-native full-stack web application that helps
software engineering candidates prepare for technical interviews using
AI-powered tools such as resume analysis, mock interviews, coding
challenges, and personalized feedback.

The application follows a client-server architecture where the React
frontend communicates with a Flask REST API backend. The backend manages
authentication, business logic, database operations, AI integrations, and
file storage through PostgreSQL, AWS services, and the OpenAI API.

## Table of Contents

- High-Level Architecture
- Authentication Flow
- Resume Upload Flow
- AI Processing
- Database Architecture
- Deployment Architecture

---

## High-Level Architecture

![Architecture](../design/Architecture/Overview.png)

> Editable source: [architecture.drawio](../design/Architecture/Overview.drawio)