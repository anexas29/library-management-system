# Library Management System

A comprehensive web-based library management system built with FastAPI backend and vanilla HTML/CSS/JavaScript frontend. This system allows librarians and users to manage books, memberships, transactions, and generate reports efficiently.

## Features

### User Management
- Role-based access (Admin and User)
- Secure authentication with JWT tokens
- Default admin and user accounts

### Book Management
- Add, update, and manage book inventory
- Track book availability and status

### Membership Management
- Create and manage user memberships
- Different membership types and privileges

### Transactions
- Issue books to members
- Return books with due date tracking
- Overdue book management
- Fine calculation and reporting

### Reports
- Issued books report
- Fine collection report
- Overdue returns tracking

### Admin Dashboard
- User management
- System maintenance
- Report generation

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Database (easily configurable for other databases)
- **PyMySQL**: MySQL connector (optional)
- **Python-Jose**: JWT token handling
- **PassLib**: Password hashing
- **Uvicorn**: ASGI server

### Frontend
- **HTML5**: Structure
- **CSS3**: Styling
- **Vanilla JavaScript**: Interactivity and API calls

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- Web browser

## Installation

1. **Clone or download the project**
   ```bash
   cd path/to/your/projects
   # If downloaded as zip, extract to library-management-system
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## Running the Application

### Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Run the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```

   The backend will be available at: http://localhost:8000

   API documentation: http://localhost:8000/docs (Swagger UI)

### Frontend
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Start a simple HTTP server:
   ```bash
   # Python 3.x
   python -m http.server 3000
   ```

   The frontend will be available at: http://localhost:3000

3. Open your browser and go to: http://localhost:3000/login.html

## Default Credentials

- **Admin**: username: `admin`, password: `admin`
- **User**: username: `user`, password: `user`

## API Endpoints

The system provides RESTful API endpoints for all operations:

- `POST /auth/login`: User authentication
- `GET /admin/*`: Admin operations (user management, reports)
- `GET /user/*`: User operations (book search, personal transactions)
- `POST /maintenance/*`: Book and membership management
- `POST /transactions/*`: Issue/return books
- `GET /reports/*`: Generate reports

## Database

The application uses SQLite by default (`library.db`). To use MySQL:

1. Install MySQL server
2. Update `DATABASE_URL` in `app/database.py`:
   ```python
   DATABASE_URL = "mysql+pymysql://username:password@localhost/library_db"
   ```

## Project Structure

```
library-management-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app instance
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication utilities
│   │   ├── dependencies.py      # Dependency injection
│   │   └── routes/              # API route handlers
│   │       ├── login.py
│   │       ├── admin.py
│   │       ├── user.py
│   │       ├── maintenance.py
│   │       ├── transactions.py
│   │       └── reports.py
│   └── requirements.txt
└── frontend/
    ├── *.html                  # Main pages
    ├── css/
    │   └── style.css           # Stylesheets
    ├── js/
    │   ├── auth.js             # Authentication
    │   ├── maintenance.js      # Maintenance operations
    │   ├── reports.js          # Report generation
    │   └── transactions.js     # Transaction handling
    └── subdirectories/         # Page-specific folders
```

## Development

### Running Tests
```bash
# Backend tests (if implemented)
cd backend
python -m pytest
```

### Code Formatting
```bash
# Install black and isort
pip install black isort

# Format code
black .
isort .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to use and modify as needed.

## Support

For issues or questions:
- Check the API documentation at `/docs`
- Review the code comments
- Open an issue in the repository

---

Built with ❤️ using FastAPI and modern web technologies.</content>
<parameter name="filePath">c:\Users\saxen\OneDrive\Desktop\library-management-system\library-management-system\README.md
