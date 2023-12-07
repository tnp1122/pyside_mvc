class UserListTableController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def set_table_items(self, user_list):
        self.model.user_list = user_list
        self.view.set_table_items(self.model.user_list)

    def clear_table_items(self):
        self.model.user_list = []
        self.view.clear_table()
