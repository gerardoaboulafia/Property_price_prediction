from db_utils import get_connection, upload_csv_to_mysql

conn = get_connection(password="ameagusmica", port=3307, database="laboratorioII")
upload_csv_to_mysql("data/raw/properaty_dataset_alumnos.csv", "raw_data", conn)
conn.close()
