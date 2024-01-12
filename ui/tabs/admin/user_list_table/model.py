class UserListTableModel:
    def __init__(self):
        self._user_list = []

    @property
    def user_list(self):
        return self._user_list

    @user_list.setter
    def user_list(self, value):
        self._user_list = value
