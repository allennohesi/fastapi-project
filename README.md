# FastAPI User Management System

A RESTful API built with FastAPI for user management with token-based authentication.

## Features

- ✅ User registration and authentication
- ✅ Token-based authorization
- ✅ CRUD operations for users
- ✅ Password hashing with bcrypt
- ✅ MySQL database integration
- ✅ Interactive API documentation (Swagger UI)

## Tech Stack

- **Framework**: FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Authentication**: Token-based (stored in database)
- **Password Hashing**: Passlib with bcrypt

## Installation

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd "From Scratch fastapi"
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment
**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install fastapi uvicorn sqlalchemy pymysql passlib[bcrypt] python-jose[cryptography] python-multipart email-validator
```

### 5. Configure database
Update `database.py` with your MySQL credentials:
```python
DB_USER = "root"
DB_PASS = ""  # Your MySQL password
DB_HOST = "127.0.0.1"
DB_NAME = "fastapisample"
```

### 6. Create database
```sql
CREATE DATABASE fastapisample;
```

### 7. Create tables
```bash
python create_tables.py
```

### 8. Run the application
```bash
uvicorn fast:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Endpoints

### Authentication (No token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get token |

### Authentication (Token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/logout` | Logout and invalidate token |

### Users (Token required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create a new user |
| GET | `/users` | Get all users |
| GET | `/users/{user_id}` | Get user by ID |
| PUT | `/users/{user_id}` | Update user |
| DELETE | `/users/{user_id}` | Delete user |

### Other

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/items/{item_id}` | Get item (demo) |
| GET | `/test-db` | Test database connection |

## Usage Examples

### 1. Register a new user
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123"
  }'
```

### 2. Login to get token
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "token": "your-token-here",
  "user_id": 1,
  "message": "Login successful"
}
```

### 3. Use token to access protected endpoints
```bash
curl -X GET "http://127.0.0.1:8000/users" \
  -H "Authorization: Bearer your-token-here"
```

## Database Schema

### user_tbl
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| first_name | String(100) | User's first name |
| middle_name | String(100) | User's middle name (optional) |
| last_name | String(100) | User's last name |
| email | String(255) | User's email (unique) |
| hashed_password | String(255) | Hashed password |
| is_active | Boolean | Account status |

### auth_token
| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key (auto-increment) |
| user_id | Integer | Foreign key to user_tbl |
| token | String(255) | Authentication token (unique) |

## Project Structure

```
From Scratch fastapi/
├── fast.py              # Main application file
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── create_tables.py     # Database table creation script
├── .gitignore           # Git ignore file
├── README.md            # Project documentation
└── venv/                # Virtual environment (not in git)
```

## Security Features

- ✅ Password hashing using bcrypt
- ✅ Token-based authentication
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ Email validation
- ✅ Duplicate email prevention
- ✅ One token per user policy

## Development

### Running in development mode
```bash
uvicorn fast:app --reload
```

### Creating new database tables
After modifying `models.py`, run:
```bash
python create_tables.py
```

## License

This project is open source and available for educational purposes.

## Contributing

Feel free to submit issues and pull requests.

## Author

Your Name

## Acknowledgments

- FastAPI - https://fastapi.tiangolo.com/
- SQLAlchemy - https://www.sqlalchemy.org/
- Passlib - https://passlib.readthedocs.io/

"# fastapi-project" 
