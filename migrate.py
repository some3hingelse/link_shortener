import sys

from database import Database, DatabaseMigrator

if __name__ == "__main__":
    db = Database()
    db_migrator = DatabaseMigrator(db)

    if len(sys.argv) < 2:
        raise Exception("Usage: python migrate.py upgrade/downgrade")

    if sys.argv[1] == "upgrade":
        db_migrator.upgrade()
    if sys.argv[1] == "downgrade":
        db_migrator.downgrade()
