from db_worker import db_connector, db_url_creator
import csv
from sqlalchemy import text, insert, select, update


engine, Base, SessionLocal = db_connector(db_url_creator(
    "postgresql", "postgres", "postgres", "localhost", "5432", "films_rating"))


def load_tsv_to_database(filepath, table_name, engine, session_local):
    """Loads data from a TSV file into a specified database table.

    Args:
        filepath (str): Path to the TSV file.
        table_name (str): Name of the database table.
        engine: SQLAlchemy engine object.
        session: SQLAlchemy session object.
    """
    try:
        with session_local() as session:
            with open(filepath, 'r', encoding='utf-8') as tsvfile:
                reader = csv.DictReader(
                    tsvfile, delimiter='\t')  # Note the delimiter

                first_row = next(reader)
                columns = list(first_row.keys())

                column_types = {
                    "tconst": "TEXT",
                    "averageRating": "FLOAT",  # Or NUMERIC if you need more precision
                    "numVotes": "INTEGER"
                }

                create_table_query = f"CREATE TABLE IF NOT EXISTS {
                    table_name} ("
                for col in columns:
                    # Default to TEXT if type is unknown. Handle other types as appropriate
                    create_table_query += f"{col} {
                        column_types.get(col, 'TEXT')}, "
                create_table_query = create_table_query.rstrip(", ") + ")"

                with engine.connect() as conn:
                    conn.execute(text(create_table_query))
                    session.commit()

                tsvfile.seek(0)
                next(reader)  # To skip header row after seek

                for row in reader:
                    columns = ', '.join(row.keys())
                    placeholders = ', '.join(['%s'] * len(row))
                    values = tuple(row.values())
                    insert_query = f"INSERT INTO {
                        table_name} ({columns}) VALUES ({placeholders})"
                    with engine.connect() as conn:
                        conn.execute(text(insert_query), values)
                        session.commit()

        print(f"Data from '{filepath}' loaded into table '{table_name}'")

    except Exception as e:
        print(f"Error loading TSV: {e}")


# Replace with your file path
tsv_filepath = "/home/tikhon/Загрузки/title_ratings.tsv"
table_name = "films_rating"  # Replace with your table name

load_tsv_to_database(tsv_filepath, table_name, engine, SessionLocal)
