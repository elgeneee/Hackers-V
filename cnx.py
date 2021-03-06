import pyodbc
import pandas as pd
import os
import pathlib
# Some other example server values are
# server = 'localhost\sqlexpress' # for a named instance
# server = 'myserver,port' # to specify an alternate port


def connection():
    server = 'hackersv.database.windows.net'
    database = 'hackersv'
    username = 'hackersv2021'
    password = '$2021hackersv'
    cnx = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                         server+';DATABASE='+database+';UID='+username+';PWD=' + password)
    return cnx


def newUserID():
    cnx = connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT MAX(userID) FROM [users]')
    rows = cursor.fetchall()
    userId = rows[0][0]
    cursor.close()
    cnx.close()
    if len(rows) == 0:
        return 1
    else:
        return userId + 1


def newUser(firstName, lastName, email, password, occupation, phoneNum, location, image):
    if (firstName == "" or lastName == "" or email == "" or password == ""):
        message = "Fields cannot be null"
        return message
    cnx = connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM [users] WHERE email = ?', email)
    data = cursor.fetchall()
    if len(data) != 0:
        message = "User exists in database"
        return message
    else:
        usrId = newUserID()
        cnx = connection()
        cursor = cnx.cursor()
        cursor.execute('INSERT INTO [users] VALUES (?,?,?,?,?,?,?,?,?)', usrId, firstName, lastName, email, password, occupation, phoneNum, location, image)
        cnx.commit()
        message = "Account Created"
        return message


def login(email, logPass):
    accPass = ""
    cnx = connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM [users] WHERE email = ?', email)
    data = cursor.fetchall()
    for row in data:
        accPass = row.password
    if (logPass == accPass):
        return True
    else:
        return False


def getUser(email):
    cnx = connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM [users] WHERE email = ?', email)
    data = cursor.fetchall()
    return data

def updateUser(email, firstName, lastName, occupation, phoneNum, location, imgDir):
    if (firstName == "" or lastName == "" or email == ""):
        message = "Fields cannot be null"
        return message
    else:
        cnx = connection()
        cursor = cnx.cursor()
        cursor.execute('UPDATE users SET firstName = ?, lastName = ?, occupation = ?, phoneNum = ?, location = ? WHERE email = ?',
                       firstName, lastName, occupation, phoneNum, location, email)
        cnx.commit()
        message = "Account Updated"
        return message

def uploadBonds(fileDir):
    data = pd.read_csv(fileDir)
    df = pd.DataFrame(data, columns=['VALUE DATE', 'STOCK CODE', 'EVAL MID YIELD', 'COMPOSITE LIQUIDITY SCORE (T-1)', 'COUPON FREQUENCY', 'NEXT COUPON RATE', 'CALLABLE/PUTTABLE', 'MODIFIED DURATION', 'EVAL MID PRICE', 'REMAINING TENURE', 'OUTPUT PRICE',
                                     'RATING TARGET', 'OPR level'])
    # Insert DataFrame to Table
    cnx = connection()
    cursor = cnx.cursor()
    for row in df.itertuples():
        cursor.execute("INSERT INTO bonds VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", row._1, row._2, row._3,
                       row._4, row._5, row._6, row._7, row._8, row._9, row._10, row._11, row._12, row._13)
    cnx.commit()
    return True


def uploadSortedBonds(fileDir):
    i = 1
    data = pd.read_csv(fileDir)
    df = pd.DataFrame(data, columns=[
                      'Stock Code', 'Monthly Average Return', 'Volatility', 'Return/ Volatility Ratio'])
    # Insert DataFrame to Table
    cnx = connection()
    cursor = cnx.cursor()
    for row in df.itertuples():
        cursor.execute("INSERT INTO sortedbonds VALUES (?,?,?,?,?)",
                       i, row._1, row._2, row.Volatility, row._4)
        i += 1
    cnx.commit()
    return True


def downloadBonds():
    SQL_Query = pd.read_sql_query('SELECT * from bonds', connection())
    df = pd.DataFrame(SQL_Query, columns=['VALUE_DATE', 'STOCK_CODE', 'EVAL_MID_YIELD', 'COMPOSITE_LIQUIDITY_SCORE', 'COUPON_FREQUENCY', 'NEXT_COUPON_RATE', 'CALLABLE', 'MODIFIED_DURATION', 'EVAL_MID_PRICE', 'REMAINING_TENURE', 'OUTPUT_PRICE',
                                          'RATING_TARGET', 'OPR_LEVEL'])
    return df


def downloadsortedBonds():
    SQL_Query = pd.read_sql_query('SELECT * from sortedbonds', connection())
    df = pd.DataFrame(SQL_Query, columns=[
                      'RATING', 'STOCK_CODE', 'MONTHLY_AVERAGE_RETURN', 'VOLATILITY', 'RETURN_RATIO'])
    return df


def getBond(bondName):
    cnx = connection()
    cursor = cnx.cursor()
    cursor.execute('SELECT * FROM bonds WHERE STOCK_CODE = ?', bondName)
    data = cursor.fetchall()
    return data


def searchBond(bondName):
    df = downloadBonds()
    subFrame = df.loc[df['STOCK_CODE'].str.contains(bondName, case=False)]
    if(len(subFrame) == 0):
        return "No bonds found"
    else:
        records = subFrame.to_records(index=False)
        result = list(records)
        return result


def sortedBonds(topNo):
    query = 'SELECT * from sortedbonds WHERE RATING <= ' + str(topNo)
    SQL_Query = pd.read_sql_query(query, connection())
    df = pd.DataFrame(SQL_Query, columns=[
                      'RATING', 'STOCK_CODE', 'MONTHLY_AVERAGE_RETURN', 'VOLATILITY', 'RETURN_RATIO'])
    records = df.to_records(index=False)
    result = list(records)
    return result


def uploadImg(imgDir, email):
    cnx = connection()
    cursor = cnx.cursor()
    # save binary file
    with open(imgDir, 'rb') as photo_file:
        photo_bytes = photo_file.read()
    cursor.execute("UPDATE users SET image = ? WHERE email = ?",
                   photo_bytes, email)
    cnx.commit()
    return(f'{len(photo_bytes)}-byte file written for {email}')


def downloadImg(email):
    cnx = connection()
    cursor = cnx.cursor()
    # retrieve binary data and save as new file
    retrieved_bytes = cursor.execute(
        "SELECT image FROM users WHERE email = ?", email).fetchval()
    pdir = pathlib.Path().resolve()
    os.remove(str(pdir) + '\\static\\assets\\profile\\elgene.jpg')
    with open(str(pdir) + '\\static\\assets\\profile\\elgene.jpg', 'wb') as new_jpg:
        new_jpg.write(retrieved_bytes)
    return (f'{len(retrieved_bytes)} bytes retrieved and written to new file')
    # 5632 bytes retrieved and written to new file
