# Special Dates Tracker

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

## Team Members

- [Team Member 1] - AI Integration
- [Team Member 2] - API Integration
- [Team Member 3] - Security Implementation