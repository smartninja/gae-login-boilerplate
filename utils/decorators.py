from models.user import User


def login_required(handler):
    def check_login(self, *args, **kwargs):
        user = User.get_current_user(request=self.request, response=self.response)

        if user:
            self.user = user
            return handler(self, *args, **kwargs)
        else:
            return self.redirect("/login?destination={}".format(self.request.path))

    return check_login
