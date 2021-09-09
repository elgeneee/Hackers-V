from flask import Flask, render_template, url_for, request, redirect, flash
import urllib.request
import json
import os
import ssl
import cnx


app = Flask(__name__)

userEmail = ""


def fillTable(tableType, keyword):
    if (tableType == "bonds"):
        headings = ('VALUE DATE', 'STOCK CODE', 'EVAL MID YIELD', 'COMPOSITE LIQUIDITY SCORE (T-1)', 'COUPON FREQUENCY', 'NEXT COUPON RATE',
                    'CALLABLE/PUTTABLE', 'MODIFIED DURATION', 'EVAL MID PRICE', 'REMAINING TENURE', 'OUTPUT PRICE', 'RATING TARGET', 'OPR level')
        data = cnx.searchBond(keyword)
        return (headings, data)
    elif(tableType == "sortedbonds"):
        headings = ('Rating', 'Stock Code', 'Monthly Average Return',
                    'Volatility', 'Return/ Volatility Ratio')
        data = cnx.sortedBonds(keyword)
        return (headings, data)


@app.route('/', methods =["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form["email"]
        pw = request.form["password"]

        #validate user
        if cnx.login(email,pw):
            global userEmail
            userEmail = email
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html')

    else:
        return render_template('index.html')

@app.route('/dashboard', methods =["GET", "POST"])
def dashboard():
    if request.method == "POST":
        value_date = request.form["value_date"] + "-T00:00:000Z"
        stock_code = request.form["stock_code"]
        eval_mid_yield = request.form["eval_mid_yield"]
        composite_liquidity_score = request.form["composite_liquidity_score"]
        coupon_frequency = request.form["coupon_frequency"]
        next_coupon_rate = request.form["next_coupon_rate"]
        modified_duration = request.form["modified_duration"]
        eval_mid_price = request.form["eval_mid_price"]
        rating = request.form["rating"]
        remaining_tenure = request.form["remaining_tenure"]
        opr_level = request.form["opr_level"]
        final_price = predict_price(value_date, stock_code, eval_mid_yield, composite_liquidity_score, coupon_frequency, next_coupon_rate, modified_duration, eval_mid_price, rating, remaining_tenure, opr_level)
        return render_template('dashboard.html', predicted_price=final_price)
    else:
        return render_template('dashboard.html')

@app.route('/recommendation')
def recommendation():
    genTable = fillTable("sortedbonds", 5)
    return render_template('recommendation.html', headings=genTable[0], data=genTable[1])
        
@app.route('/profile')
def profile():
    data = cnx.getUser(userEmail)
    if(len(data)==0):
        return render_template('profile.html')
    if(data[0][8]!=None):
        cnx.downloadImg(userEmail)
    return render_template('profile.html', name=(data[0][1] + " " + data[0][2]), occupation=data[0][5], firstname=data[0][1], lastname=data[0][2],
                           phoneNum=data[0][6], email=data[0][3], location=data[0][7])

@app.route('/upgrade')
def upgrade():
    return render_template('upgrade.html')

@app.route('/edit-profile', methods =["GET", "POST"])
def edit_profile():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        occupation = request.form["occupation"]
        imgdir = ""
        phonenum = request.form["phonenum"]
        location = request.form["states"]
        cnx.updateUser(userEmail, firstname, lastname, occupation, phonenum, location, imgdir)
        return profile()
    else:
        return render_template('edit-profile.html')

@app.route('/sign-up', methods =["GET", "POST"])
def sign_up():
    if request.method == "POST":
        
        email = request.form["email"]
        password = request.form["password"]

        mssg = cnx.newUser("null", " ", email, password, "null", "null", "null", None)
        global userEmail
        userEmail = email
        print(mssg)
        if mssg == "Account Created":
            return redirect(url_for('dashboard'))
        else:
            return render_template('sign-up.html')
    else:
        return render_template('sign-up.html')

def predict_price(valueDate, stockCode, evalMidYield, compositeLiquidityScore, couponFrequency, nextCouponRate, modifiedDuration, evalMidPrice, rating, remainingTenure, oprLevel):
    data = {
        "data":
        [
            {
                'VALUE DATE': valueDate,
                'STOCK CODE': stockCode,
                'EVAL MID YIELD': evalMidYield,
                'COMPOSITE LIQUIDITY SCORE (T-1)': compositeLiquidityScore,
                'COUPON FREQUENCY': couponFrequency,
                'NEXT COUPON RATE': nextCouponRate,
                'CALLABLE/PUTTABLE': "0",
                'MODIFIED DURATION': modifiedDuration,
                'EVAL MID PRICE': evalMidPrice,
                'REMAINING TENURE': remainingTenure,
                'RATING TARGET': rating_converter(rating),
                'OPR level': oprLevel,
            },
        ],
    }

    body = str.encode(json.dumps(data))

    url = 'http://cd9dd097-7aa9-447a-9a7b-5fb84ef81109.southeastasia.azurecontainer.io/score'
    api_key = ''
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        Dict = eval(result)
        tempVar = "%.3f" % Dict['forecast'][0]
        return(tempVar)
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))
        return "Error! Try Again"

def rating_converter(rating):
    rating_dict={'AA1': 107.24783506493489,'AAA': 105.7042790530845,'AA1 (S)': 104.46866666666664,
             'A+ IS': 101.53229017857136,'AAA IS': 105.929512137823,'AA-': 103.09835433070864,
             'AA- IS': 107.60401244167973,'AA3': 107.3988118169398,'A2': 93.0150110713705,
             'A3': 92.11614515213665,'AA': 103.49153521126759,'A-': 109.7028819733158,
             'A- IS': 102.13877777777778,'A1': 102.95920889748545,'AA2': 105.78918779342717,
             'AAA (S)': 106.64285897435897,'AA2 (S)': 103.18033009708738,'AA+ IS': 105.16878928571433,
             'A IS': 97.81115934065929,'AA IS': 108.35273076923077,'AA3 (S)': 101.78773710993016}
    try:
        value = rating_dict[rating]
        return value
    except KeyError:
        return 100

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
