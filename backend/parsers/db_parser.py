import db.db_worker as db_worker


def db_parser(db_type, user, password, host, port, database):
    """Создает подключение к базе данных и возвращает engine, Base, SessionLocal.

    Args:
        db_type (str): Тип базы данных (например, "postgresql").
        user (str): Имя пользователя базы данных.
        password (str): Пароль пользователя базы данных.
        host (str): Адрес хоста базы данных.
        port (int or str): Порт базы данных.
        database (str): Имя базы данных.

    Returns:
        tuple: Кортеж, содержащий движок SQLAlchemy (engine), базовый класс для
               объявления моделей (Base) и фабрику сессий (SessionLocal).
               Возвращает None в случае ошибки.
    """
    engine, Base, session = db_worker.db_connector(db_worker.db_url_creator(
        db_type, user, password, host, port, database))
    # db_connector(engine)
    db_worker.export_data_to_file(engine=engine, table_name="films_rating")


if __name__ == "__main__":
    db_parser("postgresql", "postgres", "postgres",
              "localhost", "5432", "films_rating")
