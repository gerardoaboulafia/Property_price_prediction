import mysql.connector
import pandas as pd

def get_connection(user="root", password="tu_password", host="localhost", port=3307, database="proyectos"):
    """
    Crea la conexión con MySQL y devuelve el objeto connection.
    Ajusta user/password/host/port/database según tu instalación.
    """
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        database=database
    )

def upload_csv_to_mysql(csv_path, table_name, connection):
    """
    Carga un CSV a MySQL en la tabla especificada.
    Sobrescribe si la tabla ya existe.
    """
    df = pd.read_csv(csv_path)

    cursor = connection.cursor()
    # Crear tabla genérica (ajustá los tipos según tu necesidad)
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cols = ", ".join([f"`{col}` TEXT" for col in df.columns])
    cursor.execute(f"CREATE TABLE {table_name} ({cols})")

    # Insertar filas
    for _, row in df.iterrows():
        placeholders = ", ".join(["%s"] * len(row))
        cursor.execute(
            f"INSERT INTO {table_name} VALUES ({placeholders})",
            tuple(row.astype(str))
        )
    connection.commit()
    cursor.close()
    print(f"CSV subido a la tabla {table_name}")

def download_from_mysql(table_name, connection):
    """
    Descarga una tabla de MySQL como DataFrame de pandas.
    """
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, connection)
    return df

def upload_dataframe_to_mysql(df, table_name, connection):
    """
    Sube un DataFrame ya procesado a MySQL en la tabla especificada.
    """
    cursor = connection.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cols = ", ".join([f"`{col}` TEXT" for col in df.columns])
    cursor.execute(f"CREATE TABLE {table_name} ({cols})")

    for _, row in df.iterrows():
        placeholders = ", ".join(["%s"] * len(row))
        cursor.execute(
            f"INSERT INTO {table_name} VALUES ({placeholders})",
            tuple(row.astype(str))
        )
    connection.commit()
    cursor.close()
    print(f"DataFrame subido a la tabla {table_name}")
