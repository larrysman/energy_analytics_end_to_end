# ================ LOAD TO MYSQL =============== #

import yaml
from sqlalchemy import create_engine, text

from src.generate_and_load_data_01 import generate_and_load_data

# FUNCTION TO LOAD DATABASE CONFIGURATION FROM YAML FILE AND CONNECT TO MYSQL DATABASE -> THIS FUNCTION ALSO CHECKS IF THE DATABASE EXISTS AND CREATES IT IF IT DOES NOT EXIST
def load_db_config(config_path="../config/mysql_db_config.yaml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config["mysql"]

def get_mysql_engine(config_path="../config/mysql_db_config.yaml"):
    config = load_db_config(config_path)
    # CREATE A TEMPORARY ENGINE WITHOUT THE DATABASE TO ENSURE THE DATABASE EXISTS
    uri = (
        f"mysql+pymysql://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}"
    )
    temp_engine = create_engine(uri)

    # CREATE DATABASE IF NOT EXISTS
    with temp_engine.connect() as connection:
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {config['database']}"))
    
    # NOW CREATE THE ENGINE WITH THE DATABASE INCLUDED
    full_uri = f"{uri}/{config['database']}"
    engine = create_engine(full_uri)
    
    return engine

if __name__ == "__main__":
    # GENERATE THE DATA
    energy_data = generate_and_load_data()
    
    # INSTANTIATE THE DATABASE ENGINE AND THE CONFIGURATION
    mysql_engine = get_mysql_engine()
    db_config = load_db_config()
    database_name = db_config["database"]

    # LOAD DATAFRAME TO MYSQL DATABASE
    table_name = "energy_consumption_data"

    # LOAD THE DATAFRAME TO MYSQL DATABASE IN CHUNKS TO HANDLE LARGE DATASETS -> THIS IS MORE EFFICIENT AND PREVENTS MEMORY ISSUES
    from math import ceil

    CHUNK_SIZE = 5000
    NO_CHUNKS = ceil(len(energy_data) / CHUNK_SIZE)

    for k in range(NO_CHUNKS):
        CHUNK = energy_data.iloc[k*CHUNK_SIZE:(k+1)*CHUNK_SIZE]

        CHUNK.to_sql(table_name, mysql_engine, if_exists="append" if k > 0 else "replace", index=False, method="multi")

        print(f"Chunk {k+1}/{NO_CHUNKS} loaded successfully.")


    