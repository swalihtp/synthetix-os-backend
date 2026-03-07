## Synthetix OS – AI-Powered Automation Platform

Synthetix OS is an intelligent automation platform that acts as a digital employee, allowing users to automate tasks across applications like Gmail, Google Sheets, and Telegram using AI-powered agents.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Django](https://img.shields.io/badge/Django-Backend-green)
![React](https://img.shields.io/badge/React-Frontend-blue)
![Status](https://img.shields.io/badge/Status-Active-success)

## Why Synthetix OS?

Instead of manually switching between apps and repeating tasks, Synthetix OS allows users to automate real-world workflows using AI agents.

👉 Example:
When a new email arrives → AI reads it → generates a reply → sends it automatically.

This reduces manual work and improves productivity.

##  Problem

Modern workflows require switching between multiple applications and performing repetitive tasks manually.

Examples:
- Responding to emails
- Updating spreadsheets
- Managing schedules
- Handling customer queries

This leads to:
- Time consumption
- Human errors
- Low productivity

##  Solution

Synthetix OS introduces AI Agents that can:

- Think using AI
- Remember past interactions
- Perform actions across apps
- Execute workflows automatically

It acts like a digital employee working on behalf of the user.

##  Features

-  AI Agents (Digital Employees)
-  Memory System (Context-aware AI)
-  Workflow Automation
-  Trigger System (Webhook, Schedule, Events)
-  Integrations (Gmail, Google Sheets, Telegram)
-  Secure OAuth-based Access
-  Scalable Architecture (Celery, Redis)


## Architecture

User → Trigger → Workflow → Agent → AI → Action → Result

Components:
- Agent Module (Brain)
- Workflow Engine (Execution)
- Trigger System (Start events)
- Integration Layer (External apps)

## Tech Stack

Backend:
- Python
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery

Frontend:
- React.js

AI:
- LLM APIs
- Embeddings (Vector Search)

Infrastructure:
- Docker (planned)
- Cloud Deployment


## Project Structure (Backend)

accounts/        # Authentication & users
agents/          # Agent management
workflows/       # Workflow engine
triggers/        # Trigger system
executions/      # Workflow execution tracking
integrations/    # External APIs (Gmail, etc.)
ai/              # LLM interaction
common/          # Shared utilities


## Setup Instructions

### 1. Clone the repository
git clone https://github.com/your-username/synthetix-backend.git

### 2. Navigate
cd synthetix-backend

### 3. Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

### 4. Install dependencies
pip install -r requirements.txt

### 5. Setup environment variables
cp .env.example .env

### 6. Run migrations
python manage.py migrate

### 7. Start server
python manage.py runserver

## Environment Variables

Create a `.env` file:

SECRET_KEY=your_secret
DEBUG=True

DB_NAME=...
DB_USER=...
DB_PASSWORD=...

OPENAI_API_KEY=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

## 📡 API Endpoints

Auth:
POST   /api/auth/register/
POST   /api/auth/login/

Agents:
POST   /api/agents/
GET    /api/agents/

Workflows:
POST   /api/workflows/

Triggers:
POST   /api/triggers/

Webhook:
POST   /api/triggers/webhook/{path}/


## Roadmap

- [x] Authentication system
- [x] Agent management module
- [x] Workflow engine (basic)
- [ ] Trigger system (in progress)
- [ ] Gmail integration
- [ ] Google Sheets automation
- [ ] AI decision engine improvements
- [ ] Multi-agent collaboration
- [ ] SaaS billing system


## Screenshots

Coming soon...

## License

MIT License

## Future Vision

Synthetix OS aims to become a full AI workforce platform where multiple agents collaborate to handle business operations autonomously.

## Status

This project is currently under active development.