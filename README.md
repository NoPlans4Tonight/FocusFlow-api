# FocusFlow API

FocusFlow API is a Django-based backend application designed to help users track their activities and contexts. It provides endpoints for logging, updating, retrieving, and deleting context entries, as well as user authentication and registration. Mainly built to be used with FocusFlow-Ui.

## Features
- User authentication (login, logout, registration)
- Context tracking (log, update, retrieve, delete)
- JWT-based authentication for secure API access

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL (or any other database supported by Django)
- Virtual environment tool (optional but recommended)

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd focusflow-api
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the Database**
   - Update the `DATABASES` setting in `settings.py` with your database credentials.

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a Superuser (Optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```

8. **Access the API**
   - The API will be available at `http://127.0.0.1:8000/`.

## Testing the API
- Use tools like Postman or cURL to test the endpoints.
- Ensure you include the JWT token in the `Authorization` header for protected routes.

## Notes
- For production, configure environment variables and use a production-ready server like Gunicorn or uWSGI.
- Ensure proper security settings for deployment (e.g., `DEBUG=False`, secure database credentials).
