from flask import session as login_session


class AuthService():

    def __init__(self):
        self.login_session = login_session

    def is_user_authorized(self):
        """ returns if user is logged in """
        return 'email' in self.login_session
