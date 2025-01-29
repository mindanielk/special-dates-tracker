# Special Dates Tracker

![image](https://github.com/user-attachments/assets/03003b51-910c-4f65-a42c-11624e37e363)

A Flask web application for tracking important dates and managing wish lists for your loved ones.

## Features

- User authentication (register/login)
- Add and manage special dates
- Create wish lists for each special date
- Dashboard view of all upcoming events
- AI-powered suggestions (coming soon)
- Calendar integration (coming soon)

## Setup Instructions

1. Clone the repository:
```bash
git clone [repository-url]
cd special-dates-tracker
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000/`

## Environment Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Generate a secure secret key:
```python
python -c "import secrets; print(secrets.token_hex(24))"
```

3. Update `.env` with your secret key and database settings

For development, the SQLite database is sufficient. For production, we'll switch to PostgreSQL later.

# Special Dates Tracker

## Developing with GitHub Codespaces

### Step 1: Open in Codespaces
1. Click the green "Code" button above
2. Select "Open with Codespaces"
3. Click "New codespace"

### Step 2: Initial Setup
Once your Codespace loads, run these commands in the terminal:

```bash
# Copy environment file
cp .env.example .env

# Generate secret key and save it
python -c "import secrets; print(secrets.token_hex(24))" >> .env

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Start the application
flask run
```

6. Click the "Ports" tab in the bottom panel
7. Look for port 5000 - it will have a link to view the application

### Collaboration Features
- **Live Share**: Click the Live Share extension icon to start a collaboration session
- **Source Control**: Use the Source Control tab to manage changes
- **Pull Requests**: Create and review PRs directly in Codespaces
- **Terminal Sharing**: Share your terminal during Live Share sessions
- **Port Forwarding**: All team members can access the running application

### Development Workflow
1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and test them

3. Commit and push your changes:
```bash
git add .
git commit -m "Description of your changes"
git push origin feature/your-feature-name
```

4. Create a Pull Request from the GitHub interface

### Environment Variables
Required environment variables in `.env`:
- `FLASK_APP=app.py`
- `FLASK_ENV=development`
- `SECRET_KEY` (generate using the command above)
- `DATABASE_URL=sqlite:///special_dates.db`

## Project Structure
```
special-dates-tracker/
├── app.py
├── requirements.txt
├── instance/
│   └── special_dates.db
├── static/
│   └── css/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── add_date.html
└── venv/
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/your-feature`)
6. Create a Pull Request
