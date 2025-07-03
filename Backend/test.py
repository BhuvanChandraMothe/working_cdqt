import pyodbc

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=server-db-1890.database.windows.net,1433;"
    "DATABASE=test_database;"
    "UID=bhuvan;"
    "PWD=Koushik@2001;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

conn = pyodbc.connect(conn_str)
if conn:
    print("Connected!")
