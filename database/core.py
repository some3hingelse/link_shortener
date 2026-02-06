import os
import sqlite3
from datetime import datetime

import utils.links
from config import DbConfig
from database.models import Link


class Database:
    def __init__(self):
        self._config = DbConfig()
        self.connection = sqlite3.connect(self._config.db_filename.get_secret_value())
        self.cursor = self.connection.cursor()

    def get_link_by_short_url(self, short_url: str) -> Link | None:
        self.cursor.execute(
            "SELECT * FROM links WHERE short_url = ? LIMIT 1",
            (utils.encrypt_aes256_base64(short_url),)
        )
        result = self.cursor.fetchone()

        if not result:
            return None
        return Link(*result)

    def create_link(self, original_url: str, short_length: int, expires_at: datetime | None = None) -> str:
        original_url_encoded = utils.encrypt_aes256_base64(original_url)
        short_url = utils.generate_random_string(short_length)
        short_url_encoded = utils.encrypt_aes256_base64(short_url)
        self.cursor.execute(
            "INSERT INTO links(short_url, original_url, expires_at, short_url_length) VALUES(?,?,?,?)",
            (short_url_encoded, original_url_encoded, expires_at, short_length,),
        )
        self.connection.commit()

        return short_url


class DatabaseMigrator:
    """
    Класс для выполнения миграций с БД
    TODO: пока не реализован откат миграции при ошибке в каком-то её запросе (SQLite не позволяет закинуть пачку запросов и автоматом её откатить в случае ошибки)
    """
    def __init__(self, db: Database):
        self._db = db
        self._migrations_dir = os.path.dirname(os.path.realpath(__file__))+"/migrations/"
        try:
            self._get_current_version()
        except sqlite3.OperationalError:
            self._create_migrations_table()

    def upgrade(self, version: int = 0):
        if version == 0:
            version = int(self._get_migrations_files()[-1].split("_")[0])

        migrations_files = self._get_needed_migrations_files(version)
        if not migrations_files:
            raise FileNotFoundError(f"The database is already the latest version")

        for migration_file in migrations_files:
            self._upgrade_to_version(migration_file)

    def downgrade(self, version: int = 0):
        migrations_files = self._get_needed_migrations_files(version, is_downgrade=True)
        if not migrations_files:
            raise FileNotFoundError(f"The database is already downgraded to version {version}")

        for migration_file in migrations_files:
            self._downgrade_to_version(migration_file)

    def _upgrade_to_version(self, migration_filename: str):
        upgrade_code = self._get_migration_code(migration_filename).split("--- downgrade")[0]
        upgrade_queries = []
        for query in upgrade_code.split(';'):
            query = query.strip()
            if query:
                upgrade_queries.append(query)

        self._execute_migration_code(upgrade_queries, migration_filename)

        migration_name = migration_filename.split("_")[-1].replace(".sql", "")
        migration_version = int(migration_filename.split("_")[0])
        self._db.cursor.execute(
            "INSERT INTO migrations(number,name) VALUES(?,?)",
            (migration_version, migration_name)
        )
        self._db.connection.commit()

    def _downgrade_to_version(self, migration_filename: str):
        downgrade_code = self._get_migration_code(migration_filename).split("--- downgrade")[-1]
        downgrade_queries = []
        for query in downgrade_code.split(';'):
            query = query.strip()
            if query:
                downgrade_queries.append(query)

        self._execute_migration_code(downgrade_queries, migration_filename)

        migration_version = int(migration_filename.split("_")[0])
        self._db.cursor.execute(
            "DELETE FROM migrations WHERE number = ?",
            (migration_version,)
        )
        self._db.connection.commit()

    def _execute_migration_code(self, code: list[str], migration_filename: str):
        for query in code:
            try:
                self._db.cursor.execute(query)
            except sqlite3.OperationalError as e:
                raise MigrationError(f"Upgrade to {migration_filename} error:\n" + e.__str__())

    def _get_migration_code(self, migration_filename: str):
        with open(self._migrations_dir+migration_filename, "r") as f:
            return f.read()

    def _get_current_version(self):
        try:
            self._db.cursor.execute("SELECT number FROM migrations ORDER BY number DESC LIMIT 1")
            return self._db.cursor.fetchone()[0]
        except IndexError:
            return 0
        except TypeError:
            return 0

    def _get_migrations_files(self):
        files = os.listdir(self._migrations_dir)

        migrations = []
        for file in files:
            if file.endswith(".sql"):
                migrations.append(file)

        migrations.sort()
        return migrations

    def _get_needed_migrations_files(self, version: int = 0, is_downgrade: bool = False) -> set[str] | None:
        files = set()
        current_version = self._get_current_version()

        for filename in self._get_migrations_files():
            migration_number = int(filename.split("_")[0])

            if is_downgrade:
                if version < migration_number <= current_version:
                    files.add(filename)
            else:
                if current_version < migration_number <= version:
                    files.add(filename)

        sorted_files = sorted(files, key=lambda x: int(x.split("_")[0]))

        if is_downgrade:
            return set(sorted_files[::-1])

        return set(sorted_files)

    def _create_migrations_table(self):
        self._db.cursor.execute("""CREATE TABLE migrations(
    number INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")


class MigrationError(Exception): pass
