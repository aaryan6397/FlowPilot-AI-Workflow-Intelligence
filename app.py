import os

from flask import Flask, render_template

from config import Config
from database.db import init_app
from routes.analytics import analytics_bp
from routes.dashboard import dashboard_bp
from routes.tasks import csrf_token, tasks_bp


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    init_app(app)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(analytics_bp)
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("400.html", error=error), 400

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("500.html"), 500

    @app.cli.command("init-db")
    def init_database_command():
        from database.db import init_db
        init_db()
        print("Database initialized.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])
