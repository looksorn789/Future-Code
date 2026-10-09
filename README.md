# Future Code

## Overview

Future Code is a full-stack AI-powered interview preparation platform designed to help software engineering candidates prepare for technical and behavioral interviews.

The platform uses a user's resume, career goals, and preparation history to generate personalized interview experiences, including technical questions, coding challenges, mock interviews, and AI-powered feedback.

The project is being developed with a focus on practical AI engineering, scalable backend architecture, and cloud deployment.

## Features (Planned)

### Authentication

- Secure user authentication with Amazon Cognito
- Google and GitHub OAuth
- Email verification and password recovery
- Protected routes and role-based authorization

### Resume Analysis

- Upload resumes securely to Amazon S3
- Extract skills, education, projects, and technologies using AI
- Generate a personalized user profile
- Use resume information to personalize interview preparation

### Personalized Interview Plans

Generate interview questions tailored to a user's:

- Programming languages
- SQL knowledge
- Data Structures & Algorithms
- System Design
- Behavioral interview experience
- Desired job role

Interview plans are customized using the user's resume, career goals, and areas for improvement.

### AI Coding Coach

Practice coding interview questions with AI-assisted guidance.

Features include:

- Personalized coding challenges
- Step-by-step hints
- Explanation of optimal solutions
- Follow-up questions
- AI-generated feedback on solutions

### AI Mock Interviews

Conduct AI-powered mock interviews covering:

- Behavioral questions
- Technical questions
- Coding interviews
- Role-specific interview questions

After each session, the AI provides detailed feedback, identifies areas for improvement, and suggests topics to practice.

### Progress Dashboard

Track interview preparation through:

- Questions completed
- Coding challenges completed
- Mock interviews taken
- Strengths and weaknesses
- Progress charts
- Learning streaks

## Tech Stack

### Frontend

- React
- TypeScript
- Tailwind CSS
- Vite

### Backend

- Python
- Flask
- SQLAlchemy
- PostgreSQL

### AI

- Python
- OpenAI API
- LLM-based interview generation
- Resume analysis
- AI-powered feedback

### Cloud

- AWS Cognito
- Amazon S3
- Amazon EC2
- Amazon RDS
- CloudFront
- Route 53
- AWS Certificate Manager

### DevOps

- Docker
- GitHub Actions
- Nginx

## Architecture

Future Code follows a client-server architecture where the React frontend communicates with a Flask REST API backend.

The backend is responsible for:

- API endpoints
- Authentication
- Business logic
- Database operations
- AI integrations
- Resume processing
- Cloud storage

See the [architecture documentation](./docs/ARCHITECTURE.md) for more information.

## Project Status

Future Code is currently under active development.

The project is being developed incrementally, starting with the core application architecture and backend infrastructure before implementing the AI-powered features.

## Goals

The primary goal of Future Code is to provide a practical environment for developing and demonstrating skills in:

- Full-stack web development
- AI application development
- REST API design
- Database design
- LLM integration
- Cloud infrastructure
- Software architecture
- Containerization and deployment