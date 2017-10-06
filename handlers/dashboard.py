from handlers.base import BaseHandler
from utils.decorators import login_required


class DashboardHandler(BaseHandler):
    @login_required
    def get(self):
        params = {"user": self.user}
        return self.render_template("dashboard.html", params=params)
