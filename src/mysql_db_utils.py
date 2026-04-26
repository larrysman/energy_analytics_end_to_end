# ================ UTILITY FUNCTION FOR CONNECTING TO THE MYSQL DATABASE AND LOADING CONFIGURATION ================
import yaml
from sqlalchemy import create_engine, text


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