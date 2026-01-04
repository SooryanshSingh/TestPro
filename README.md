# Online Examination & Real-Time Proctoring System



- A production-grade online examination and real-time proctoring platform built with Django, WebSockets, and Agora RTC.

- Designed with a strong focus on real-time system behavior, secure role-based access control, and scalable 1:N exam monitoring, this project goes beyond traditional CRUD applications to solve real-world proctoring challenges.


**Deployed Link= https://testpro-z569.onrender.com/**

# Features
## Core Exam System

- Role-based authentication (Student, Test Maker, Proctor)

- MCQ-based exams

- Server-controlled exam timer (backend enforced)

- Auto submission on timeout or exam close

- Secure result calculation & storage

## Test Maker

- Create / edit / delete exams

- Bulk question creation

- Schedule exams (date, time, duration)

- Assign proctors via email

- View student marks


## Student

- Exam dashboard with question navigation

- Real-time timer synced with backend

- Tab-change detection

- Live camera streaming during exam

- Warning alerts from proctor

- Forced exam termination handling

## Proctoring (Real-Time)

- 1:N proctor dashboard

- Live list of active students

- Violation count per student

- Click-to-zoom student camera feed

- Warn student (real-time alert)

- Force close exam

## Audit & Security

- Exam audit logs (actions, actors, targets, timestamps)

- Django Groups for RBAC

- Secure WebSocket permission checks

- Environment-based secrets management



# Tech Stack

## Backend

- **Django** 

- **Django Channels**

- **PostgreSQL**

- **Whitenoise**

- **Render (Deployment)**

- **Agora RTC SDK**

- **WebSockets**

## Frontend

- HTML, CSS

- Vanilla JavaScript

- Fetch API & WebSocket API

# Environment Variables

- DJANGO_SECRET_KEY=your-secret-key
- DEBUG=False
- DATABASE_URL=postgres://...
- AGORA_APP_ID=your-agora-app-id
- AGORA_APP_CERT=your-agora-app-certificate


# Deployment

- Hosted on Render

- PostgreSQL database

- ASGI enabled for WebSockets

- Static files served via Whitenoise

# What This Project Demonstrates

- Real-time system design

- WebSocket-based communication

- Scalable video proctoring (1:N)

- Secure role-based architecture

- Production deployment readiness

- Auditability & reliability




# Design Decisions & Trade-offs

- **Why Agora instead of raw WebRTC**  
  Raw WebRTC became complex to maintain for multi-user (1:N) joins, reconnections, and ordering issues. Agora provides stable signaling, scaling, and media reliability while keeping control logic server-driven.

- **Why backend-enforced timer**  
  Client-side timers are unreliable and tamperable. Time remaining is computed server-side and polled by clients, ensuring fairness and preventing manipulation.

- **Why WebSockets over polling**  
  WebSockets allow instant propagation of proctor actions (warn, close), tab-change violations, and live dashboard updates without delay or excessive network overhead.

- **Why audit logs instead of only counters**  
  Audit logs provide traceability and post-exam review capability, essential for real-world compliance and dispute resolution.

- **Why Django Channels (ASGI)**  
  Enables a single-stack solution for HTTP + real-time communication, simplifying deployment and permission enforcement.


# Future Improvements

- Detect if no face or multiple faces appear during the exam and log it as a violation.

- Detect screen minimization, fullscreen exit, or screen sharing attempts.

- Automatically restore student exam state after accidental refresh or network drop.

- Allow proctors to add short notes during the exam for post-exam review.

- Move WebSocket channel layer to Redis for large-scale concurrent exams.


