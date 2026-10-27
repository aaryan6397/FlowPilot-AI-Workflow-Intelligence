import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE_PATH"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    database = g.pop("db", None)
    if database is not None:
        database.close()


def init_db():
    database = get_db()
    schema_path = Path(current_app.root_path) / "database" / "schema.sql"
    database.executescript(schema_path.read_text(encoding="utf-8"))
    database.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
