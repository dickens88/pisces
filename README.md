# Pisces SIEM Platform

A Security Information and Event Management (SIEM) platform with Vue.js frontend and Flask backend.

## Overview

Pisces provides security monitoring, alert management, incident tracking, and vulnerability management capabilities. The platform integrates with Huawei Cloud SecMaster for threat intelligence.

## Tech Stack

**Frontend:**
- Vue 3 + Vite
- Tailwind CSS
- Pinia (state management)
- Vue Router
- Vue I18n (Chinese & English)

**Backend:**
- Flask + Flask-RESTful
- MySQL
- JWT Authentication
- SQLAlchemy

## Quick Start

### Prerequisites
- Node.js 16+
- Python 3.8+
- MySQL 5.7+

### Backend Setup

```bash
cd api
pip install -r requirements.txt
```

Create database and import schema:
```bash
mysql -u root -p -e "CREATE DATABASE pisces_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p pisces_db < database_schema.sql
```

Configure `api/resources/config.yaml` with your database credentials.

Start backend:
```bash
python app.py
```
Backend runs on `http://localhost:8080`

### Frontend Setup

```bash
cd web
npm install
npm run dev
```
Frontend runs on `http://localhost:3000`

## Project Structure

```
pisces/
├── web/              # Vue.js frontend
│   ├── src/
│   │   ├── api/      # API services
│   │   ├── components/  # Vue components
│   │   ├── views/    # Page views
│   │   └── router/   # Routes
│   └── package.json
└── api/              # Flask backend
    ├── app.py        # Entry point
    ├── controllers/  # Business logic
    ├── models/       # Database models
    ├── views/        # API endpoints
    └── requirements.txt
```

## Features

- **Alert Management**: Monitor, filter, and manage security alerts
- **Incident Tracking**: Create and track security incidents
- **Vulnerability Management**: Track and analyze vulnerabilities
- **Dashboard**: Real-time security statistics and overview
- **Multi-language**: Chinese and English support

## Development

**Frontend:**
```bash
cd web
npm run dev      # Development server
npm run build    # Production build
```

**Backend:**
```bash
cd api
python app.py    # Development server
```

## Configuration

- Backend: Edit `api/resources/config.yaml`
- Frontend: Set `VITE_API_TARGET` in `.env` (optional, defaults to `http://localhost:8080`)

## TODO

- [ ] Authentication module development
- [ ] Dashboard development
- [ ] Incident management
- [ ] Incident details
- [ ] Alert management
- [ ] Alert details
- [ ] Vulnerability management
- [ ] Other feature improvements and enhancements
- [ ] AI Interactive

