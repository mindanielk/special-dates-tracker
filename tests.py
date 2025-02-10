from app import app, db
from app import User, Calendar, SpecialDate, WishlistItem
import json
from datetime import datetime

class TestDatabaseModels:
    def setUp(self):
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True

        with self.app.app_context():
            db.create_all()
            self.init_db()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def init_db(self):
        with self.app.app_context():
            self.user = User(username='testuser', email='testuser@gmail.com')
            self.user.set_password("password")

            self.calendar_entry = Calendar(
                date='2025-01-01',
                events=json.dumps({
                    'Birthday': {'title': 'John’s Birthday Party', 'date': '2025-01-01'}
                })
            )

            self.special_date = SpecialDate(
                title='Birthday',
                date=datetime.strptime('2025-01-01', '%Y-%m-%d'),
                category='Birthday',
                user=self.user
            )

            self.special_date_wishlist = SpecialDate(
                title="Anniversary",
                date=datetime.strptime("2025-01-02", "%Y-%m-%d"),
                category="Anniversary",
                user=self.user
            )

            self.wishlist_item = WishlistItem(
                item_name="Money",
                url="https://money.com",
                special_date=self.special_date_wishlist
            )

            db.session.add_all([
                self.user,
                self.calendar_entry,
                self.special_date,
                self.special_date_wishlist,
                self.wishlist_item
            ])
            db.session.commit()

    def test_user_creation(self):
        with self.app.app_context():
            user = db.session.get(User, 1)
            assert user is not None
            assert user.email == "testuser@gmail.com"
            assert user.check_password("password") is True
            assert user.check_password("wrongpassword") is False

    def test_calendar_entry(self):
        with self.app.app_context():
            calendar_entry = db.session.get(Calendar, "2025-01-01")
            assert calendar_entry is not None
            
            events = json.loads(calendar_entry.events)
            assert 'Birthday' in events
            assert events['Birthday']['title'] == 'John’s Birthday Party'
            assert events['Birthday']['date'] == '2025-01-01'

            all_entries = Calendar.query.filter_by(date='2025-01-01').all()
            assert len(all_entries) == 1

    def test_special_date(self):
        with self.app.app_context():
            birthday_event = SpecialDate.query.filter_by(title="Birthday").first()
            anniversary_event = SpecialDate.query.filter_by(title="Anniversary").first()

            assert birthday_event is not None
            assert birthday_event.category == "Birthday"
            assert birthday_event.user.username == "testuser"

            assert anniversary_event is not None
            assert anniversary_event.category == "Anniversary"
            assert anniversary_event.user.username == "testuser"

    def test_wishlist_item(self):
        with self.app.app_context():
            wishlist_item = WishlistItem.query.filter_by(item_name="Money").first()

            assert wishlist_item is not None
            assert wishlist_item.url == "https://money.com"
            assert wishlist_item.special_date.title == "Anniversary"

if __name__ == "__main__":
    unit_tests = TestDatabaseModels()

    unit_tests.setUp()
    try:
        print("Running test_user_creation...")
        unit_tests.test_user_creation()
        print("test_user_creation passed!")

        print("Running test_calendar_entry...")
        unit_tests.test_calendar_entry()
        print("test_calendar_entry passed!")

        print("Running test_special_date...")
        unit_tests.test_special_date()
        print("test_special_date passed!")

        print("Running test_wishlist_item...")
        unit_tests.test_wishlist_item()
        print("test_wishlist_item passed!")

    finally:
        unit_tests.tearDown()
