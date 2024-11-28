import pandas as pd
import psycopg2
from psycopg2.extras import execute_values


def create_table(cursor, table_name, columns):
    """
    Создаёт таблицу в PostgreSQL, если она не существует.

    :param cursor: курсор для работы с базой данных
    :param table_name: имя таблицы
    :param columns: список колонок и их типов данных
    """
    # Формируем SQL-запрос для создания таблицы
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join([f'{col} TEXT' for col in columns])}
    );
    """
    cursor.execute(create_query)


def load_tsv_to_postgres(tsv_file, table_name, db_params):
    """
    Загружает данные из TSV-файла в таблицу PostgreSQL.

    :param tsv_file: путь к файлу .tsv
    :param table_name: имя таблицы в PostgreSQL
    :param db_params: словарь с параметрами подключения к базе данных
    """
    # Читаем TSV-файл в DataFrame
    df = pd.read_csv(tsv_file, sep="\t")

    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(
        host=db_params['host'],
        port=db_params['port'],
        database=db_params['database'],
        user=db_params['user'],
        password=db_params['password']
    )
    cursor = conn.cursor()

    # Формируем запрос для вставки данных
    columns = list(df.columns)

    create_table(cursor, table_name, columns)

    values = [tuple(row) for row in df.to_numpy()]
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"

    try:
        # Используем execute_values для массовой вставки
        execute_values(cursor, insert_query, values)
        conn.commit()
        print(f"Данные успешно загружены в таблицу '{table_name}'.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка загрузки данных: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    # Параметры подключения к базе данных
    # "postgresql", "postgres", "postgres", "localhost", "5432", "films_rating"))

    db_params = {
        "host": "localhost",
        "port": 5432,
        "database": "films_rating",
        "user": "postgres",
        "password": "postgres"
    }

    # Имя файла и таблицы
    tsv_file = "/home/tikhon/Загрузки/title_ratings.tsv"
    table_name = "films_rating"

    load_tsv_to_postgres(tsv_file, table_name, db_params)
