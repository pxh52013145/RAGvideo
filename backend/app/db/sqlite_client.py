import sqlite3

from app.utils.paths import sqlite_db_path

def get_connection():
    return sqlite3.connect(str(sqlite_db_path()))
