from models.user import User


def login_required(handler):
    def check_login(self, *args, **kwargs):
        user = User.get_current_user(request=self.request, response=self.response)

        if user:
            self.user = user  # add user into the self object so you can access it within the handler
            return handler(self, *args, **kwargs)
        else:
            # redirect user to the login page, but remember the destination user wanted to get to
            return self.redirect("/login?destination={}".format(self.request.path))

    return check_login
