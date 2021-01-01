from sqlalchemy import create_engine

import credentials


def create_sql_engine():
    """Connects to 'fantasy' database in MySQL."""
    usr = credentials.mysql_usr
    pwd = credentials.mysql_pwd
    con = f'mysql+pymysql://{usr}:{pwd}@localhost:3306/fantasy'
    engine = create_engine(con)
    return engine


engine = create_sql_engine()
