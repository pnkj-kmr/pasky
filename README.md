# Passkey Authentication Application

A simple authentication application using WebAuthn passkeys, built with React (TypeScript) frontend and Django 5.2 backend.

## Features

- **Registration**: Users can create accounts and register passkeys
- **Login**: Users can authenticate using WebAuthn passkeys
- **Protected Routes**: Home page requires authentication
- **Modern UI**: Beautiful, responsive interface built with Tailwind CSS

## Tech Stack

### Frontend
- React 18 with TypeScript
- React Router for navigation
- Axios for API calls
- Tailwind CSS for styling
- Vite for build tooling
- WebAuthn API for passkey authentication

### Backend
- Django 5.2
- Django REST Framework
- SQLite3 database
- WebAuthn Python library for passkey verification

## Project Structure

```
pasky/
├── backend/              # Django backend
│   ├── auth_app/        # Authentication app
│   ├── config/          # Django settings
│   └── manage.py
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API services
│   │   ├── utils/       # WebAuthn utilities
│   │   └── context/     # Auth context
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- Modern browser with WebAuthn support (Chrome, Firefox, Safari, Edge)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. Start both backend and frontend servers
2. Navigate to `http://localhost:3000`
3. Click on "Register" tab
4. Enter username and email
5. Click "Register with Passkey" - your browser will prompt you to create a passkey
6. After registration, you'll be redirected to the home page
7. To login again, use the "Login" tab and enter your username
8. Click "Login with Passkey" - your browser will prompt you to authenticate

## API Endpoints

- `POST /api/auth/register/start/` - Start registration process
- `POST /api/auth/register/complete/` - Complete registration with passkey
- `POST /api/auth/login/start/` - Start login process
- `POST /api/auth/login/complete/` - Complete login with passkey
- `GET /api/auth/user/` - Get current authenticated user
- `POST /api/auth/logout/` - Logout current user

## Notes

- Passkeys require HTTPS in production (or localhost for development)
- The application uses session-based authentication
- Challenge storage is in-memory (use Redis or database in production)
- Make sure your browser supports WebAuthn API

## License

MIT License - see LICENSE file for details

