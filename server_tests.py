import json
import unittest
from model import User, Artist, Event, UserEvent, connect_to_db, db, example_data
from server import app
import server


class FlaskTests(unittest.TestCase):
    #TestCase --> testcase is created by subclassing this

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()


    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_homepage(self):
    #test functions should begin with the name 'test' so that unittest knows to auto identify the method as a test to run
        rv = self.client.get('/')
        #<Response streamed [200 OK]>
        assert 'Discover new music + go to shows' in rv.data
        #rv.data is the html, it has the actual text "" from the login html


    def login(self, email, password):
        return self.client.post('/logged-in', data=dict(
                                       email=email,
                                       password=password
                                        ), 
                                       follow_redirects=True)

    def logout(self):
        return self.client.get('/log-out', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('admin', 'default')
        assert 'you are now logged in' in rv.data
        print rv.data
        rv = self.logout()
        assert 'Goodbye, you are now logged out' in rv.data
        rv = self.login('adminx', 'default')
        assert 'Incorrect email or password, please try again' in rv.data
        rv = self.login('admin', 'defaultx')
        assert 'Incorrect email or password, please try again' in rv.data

if __name__ == '__main__':
    unittest.main() #provides a command-line interface to the test script (will say how many tets run, time it took and whether any failed)