import pyodbc

server = 'hackersv.database.windows.net'
database = 'hackersv'
username = 'hackersv2021@hackersv'
password = '$2021hackersv'
driver= '{ODBC Driver 17 for SQL Server}'

with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM [dbo].[user]")
        for row in cursor.fetchall():
            print(row)