import os
import sqlite3
from datetime import datetime

import utils.links
from config import DbConfig
from database.models import Link


class Database:
    def __init__(self):
        """Инициализирует подключение к SQLite."""
        self._config = DbConfig()
        self.connection = sqlite3.connect(self._config.db_filename.get_secret_value())
        self.cursor = self.connection.cursor()

    def get_link_by_short_url(self, short_url: str) -> Link | None:
        """
        Находит ссылку по короткому URL.

        :param short_url: Короткий URL для поиска
        :return: Объект Link или None, если ссылка не найдена
        """
        self.cursor.execute(
            "SELECT * FROM links WHERE short_url = ? AND banned IS false "
            "AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP) LIMIT 1",
            (utils.encrypt_aes256_base64(short_url),)
        )
        result = self.cursor.fetchone()

        if not result:
            return None
        return Link(*result)

    def get_all_links(self) -> list[list[str]]:
        """
        Получает все активные ссылки из базы данных.

        :return: Список ссылок в формате [id, short_url, original_url]
        """
        self.cursor.execute(
            "SELECT * FROM links WHERE banned IS false AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)",
        )
        raw_result = self.cursor.fetchall()
        processed_result = []
        for record in raw_result:
            processed_result.append([record[0], record[1], record[2]])
        return processed_result

    def create_link(self, original_url: str, short_length: int, expires_at: datetime | None = None) -> tuple[int, str]:
        """
        Создает новую короткую ссылку в базе данных.

        :param original_url: Оригинальный URL для сокращения
        :param short_length: Длина генерируемой короткой строки
        :param expires_at: Опциональная дата истечения срока действия
        :return: Кортеж (id созданной ссылки, сгенерированный короткий URL)
        :raises ShortLinkWithThatUrlAlreadyExists: Если ссылка с таким URL уже существует
        """
        original_url_encoded = utils.encrypt_aes256_base64(original_url)
        short_url = self._generate_short_url(short_length)
        short_url_encoded = utils.encrypt_aes256_base64(short_url)
        try:
            self.cursor.execute(
                "INSERT INTO links(short_url, original_url, expires_at, short_url_length) VALUES(?,?,?,?)",
                (short_url_encoded, original_url_encoded, expires_at, short_length,),
            )
            self.connection.commit()
            link_id = self.cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if e.args[0] == "UNIQUE constraint failed: links.original_url":
                raise ShortLinkWithThatUrlAlreadyExists("Short link with that url already exists")

        return link_id, short_url

    def add_click_on_link(self, link_id: int, metadata: str):
        """
        Регистрирует клик по ссылке в статистике.

        :param link_id: ID ссылки, по которой был клик
        :param metadata: Метаданные клика (User-Agent, IP и т.д.)
        """
        self.cursor.execute("INSERT INTO clicks(link_id, metadata) VALUES(?,?)", (link_id, metadata,))
        self.connection.commit()

    def _check_short_urls_pool_filled(self, length):
        self.cursor.execute("SELECT COUNT(*) FROM links WHERE short_url_length = ?", (length,))
        return self.cursor.fetchone()[0] >= length ** utils.charset_for_string_generate

    def _generate_short_url(self, length: int) -> str:
        if self._check_short_urls_pool_filled(length):
            raise ThisLengthPoolFilled("Pool of short urls with that length is filled")
        while True:
            short_url = utils.generate_random_string(length)
            if not self.get_link_by_short_url(short_url):
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
class ShortLinkWithThatUrlAlreadyExists(Exception): pass
class ThisLengthPoolFilled(Exception): pass

database = Database()

async def get_db():
    """
    Функция для dependency injection в контроллеры FastApi
    Для применения нужно обернуть аргумент функции контроллера в Depends из fastapi.param_functions
    """
    yield database
