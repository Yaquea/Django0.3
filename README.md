# Django 0.81
**A comprehensive user management application with REST API capabilities**

## Features
- **User Authentication**  
  - Email verification using Gmail SMTP
  - Session management with timeout middleware
  - System feedback through user notification messages

- **Security**  
  - Credential management using Python Decouple
  - MariaDB database backend
  - Secure password handling

- **API Endpoints**  
  Full RESTful API built with Django Rest Framework:
  ```
  │ Method   │ Endpoint              │ Description                │
  ├──────────┼───────────────────────┼────────────────────────────┤
  │ GET      │ /api/users/           │ List all users             │
  │ POST     │ /api/users/           │ Create new user            │
  │ GET      │ /api/users/{id}/      │ Get user details           │
  │ PUT      │ /api/users/{id}/      │ Update user                │
  │ DELETE   │ /api/users/{id}/      │ Delete user                │
  ```

- **Frontend**  
  - Basic Bootstrap integration
  - Static file management

## Technology Stack
- **Framework**: Django
- **Database**: MariaDB
- **API**: Django Rest Framework
- **Security**: Python Decouple for credential management
- **Email**: Gmail SMTP server
- **Frontend**: Bootstrap 5

## Known Issues
⚠️ **Resend Verification Email**  
The email verification resend view is currently non-functional.

## Installation
1. Clone repository:
   ```bash
   git clone [your-repository-url]
   ```
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   
   ```
3. Configure environment variables in `.env`:
   ```ini
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   EMAIL_HOST_PASSWORD=your_gmail_app_password
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```

## Configuration
Ensure proper SMTP setup in `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```
