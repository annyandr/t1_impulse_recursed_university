from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

def db_url_creator(db_type, user, password, host, port, database):
    db_url_template = "{db_type}://{user}:{password}@{host}:{port}/{database}"

    return db_url_template.format(
        db_type=db_type,
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )


def db_connector(db_url):
    """    Создает движок SQLAlchemy и сессию для взаимодействия с базой данных.

Args:
    db_url (str): URL подключения к базе данных. 
                    Например: "postgresql://user:password@host:port/database"

Returns:
    tuple: Кортеж, содержащий движок SQLAlchemy (engine), базовый класс для 
            объявления моделей (Base) и фабрику сессий (SessionLocal).

            Использование:
            engine, Base, SessionLocal = create_db(db_url) 
"""

    engine = create_engine(db_url)
    Base = declarative_base()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return engine, Base, SessionLocal


def export_data_to_file(table_name, filepath="output.txt"):
    """    Извлекает данные из указанной таблицы базы данных и записывает их в текстовый файл.

Args:
    table_name (str): Имя таблицы, из которой нужно извлечь данные.
    engine: Движок SQLAlchemy, полученный из функции create_db.
    filepath (str, optional): Путь к файлу, в который будут записаны данные. 
                                По умолчанию "output.txt".

Returns:
    None. Выводит сообщение об успешной записи или об ошибке.
"""
    try:
        with engine.connect() as conn:
            query = text(f"SELECT * FROM {table_name}")
            result = conn.execute(query)
            column_names = result.keys()

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(column_names)

                writer.writerows(result)

        print(f"Данные из таблицы {table_name} записаны в файл: {filepath}")
    except Exception as e:
        print(f"Возникла ошибка: {e}")


if __name__ == "__main__":
    export_data_to_file()
