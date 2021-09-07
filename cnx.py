import pyodbc
import pandas as pd
# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port


def connection():
    server = 'hackersv.database.windows.net' 
    database = 'hackersv' 
    username = 'hackersv2021' 
    password = '$2021hackersv' 
    cnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    return cnx

def newUserID():
    cnx = connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT MAX(userID) FROM [users]')
    rows = cursor.fetchall()
    if len(rows)!=0:
        return 1
    else:
        return int(rows[0][0]) + 1

def newUser(firstName, lastName, email, password, occupation, phoneNum, location, image):
    if (firstName == "" or lastName == "" or email == "" or password == ""):
        message = "Fields cannot be null"
        return message
    cnx = connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM [users] WHERE email = ?', email)
    data=cursor.fetchall()
    if len(data)!=0:
        message = "User exists in database"
        return message
    else:
        cnx = connection()
        cursor = cnx.cursor()
        cursor.execute('INSERT INTO [users] VALUES (?,?,?,?,?,?,?,?,?)', newUserID(), firstName, lastName, email, password, occupation, phoneNum, location, image)
        cnx.commit()
        message = "Account Created"
        return message

def login(email, logPass):
    accPass = ""
    cnx = connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM [users] WHERE email = ?', email)
    data=cursor.fetchall()
    for row in data:
        accPass = row.password
    if (logPass == accPass):
        return True
    else:
        return False

def uploadBonds(fileDir):
    data = pd.read_csv (fileDir)   
    df = pd.DataFrame(data, columns= ['VALUE DATE','STOCK CODE','EVAL MID YIELD','COMPOSITE LIQUIDITY SCORE (T-1)','COUPON FREQUENCY','NEXT COUPON RATE','CALLABLE/PUTTABLE','MODIFIED DURATION','EVAL MID PRICE','REMAINING TENURE','OUTPUT PRICE',
                                      'RATING TARGET','OPR level'])
    # Insert DataFrame to Table
    cnx = connection()
    cursor = cnx.cursor()
    for row in df.itertuples():
        cursor.execute("INSERT INTO bonds VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", row._1, row._2, row._3, row._4, row._5, row._6, row._7, row._8, row._9, row._10, row._11, row._12, row._13)
    cnx.commit()

def downloadBonds():
        SQL_Query = pd.read_sql_query('SELECT * from bonds', connection())
           
        df = pd.DataFrame(SQL_Query, columns=['VALUE_DATE','STOCK_CODE','EVAL_MID_YIELD','COMPOSITE_LIQUIDITY_SCORE','COUPON_FREQUENCY','NEXT_COUPON_RATE','CALLABLE','MODIFIED_DURATION','EVAL_MID_PRICE','REMAINING_TENURE','OUTPUT_PRICE',
                                      'RATING_TARGET','OPR_LEVEL'])
        return df
    
def searchBond(bondName):
    df = downloadBonds()
    subFrame = df.loc[df['STOCK_CODE'].str.contains(bondName, case=False)]
    if(len(subFrame) == 0):
        return "No bonds found"
    else:
        return subFrame

def uploadImg(imgDir, email):
    cnx = connection()
    cursor = cnx.cursor()
    # save binary file
    with open(imgDir, 'rb') as photo_file:
        photo_bytes = photo_file.read()
    cursor.execute("UPDATE users SET image = ? WHERE email = ?",  photo_bytes, email)
    print(f'{len(photo_bytes)}-byte file written for {email}')
    # 5632-byte file written for bob@example.com
    
def downloadImg(imgDir, email):
    cnx = connection()
    cursor = cnx.cursor()
    # retrieve binary data and save as new file
    retrieved_bytes = cursor.execute("SELECT image FROM users WHERE email = ?", email).fetchval()
    with open(imgDir + 'new.jpg', 'wb') as new_jpg:
        new_jpg.write(retrieved_bytes)
    print(f'{len(retrieved_bytes)} bytes retrieved and written to new file')
    # 5632 bytes retrieved and written to new file

    