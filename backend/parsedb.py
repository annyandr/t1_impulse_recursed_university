from parsers.db_parser import db_parser
from db.db_worker import db_url_creator

if __name__ == "__main__":
    db_parser("postgresql", "postgres", "postgres",
              "localhost", "5432", "films_rating")
