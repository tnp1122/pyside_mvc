class HomeModel:
    def __init__(self):
        self._username_login = ""
        self._password_login = ""
        self._username_rg = ""
        self._password_rg = ""
        self._name = ""

    @property
    def username_login(self):
        return self._username_login

    @property
    def password_login(self):
        return self._password_login

    @property
    def username_rg(self):
        return self._username_rg

    @property
    def password_rg(self):
        return self._password_rg

    @property
    def name(self):
        return self._name

    @username_login.setter
    def username_login(self, value):
        self._username_login = value

    @password_login.setter
    def password_login(self, value):
        self._password_login = value

    @username_rg.setter
    def username_rg(self, value):
        self._username_rg = value

    @password_rg.setter
    def password_rg(self, value):
        self._password_rg = value

    @name.setter
    def name(self, value):
        self._name = value
