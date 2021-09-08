from flask import Flask, render_template, url_for, request, redirect, flash
import urllib.request
import json
import os
import ssl
import cnx

app = Flask(__name__)
app.secret_key = "super secret key"


def fillTable(keyword):
    headings = ('VALUE DATE', 'STOCK CODE', 'EVAL MID YIELD', 'COMPOSITE LIQUIDITY SCORE (T-1)', 'COUPON FREQUENCY', 'NEXT COUPON RATE', 'CALLABLE/PUTTABLE', 'MODIFIED DURATION', 'EVAL MID PRICE', 'REMAINING TENURE', 'OUTPUT PRICE', 'RATING TARGET', 'OPR level')
    data = cnx.searchBond(keyword)
    return (headings, data)

@app.route('/', methods =["GET", "POST"])
def index():
    if request.method == "POST":
        return render_template('dashboard.html')

    else:
        return render_template('index.html')

@app.route('/dashboard', methods =["GET", "POST"])
def dashboard():
    genTable = fillTable("P")
    if request.method == "POST":
        value_date = request.form["value_date"] + "-T00:00:000Z"
        bond_id = 1
        eval_mid_yield = request.form["eval_mid_yield"]
        composite_liquidity_score = request.form["composite_liquidity_score"]
        coupon_frequency = request.form["coupon_frequency"]
        next_coupon_rate = request.form["next_coupon_rate"]
        modified_duration = request.form["modified_duration"]
        eval_mid_price = request.form["eval_mid_price"]
        rating = request.form["rating"]
        remaining_tenure = request.form["remaining_tenure"]
        
        final_price = predict_price(value_date, bond_id, eval_mid_yield, composite_liquidity_score, coupon_frequency, next_coupon_rate, modified_duration, eval_mid_price, rating, remaining_tenure)
        return render_template('dashboard.html', predicted_price=final_price)
    else:
        return render_template('dashboard.html', headings=genTable[0], data=genTable[1])

@app.route('/recommendation')
def recommendation():
    genTable = fillTable("PO")
    return render_template('recommendation.html', headings=genTable[0], data=genTable[1])
        
@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/upgrade')
def upgrade():
    return render_template('upgrade.html')

@app.route('/edit-profile', methods =["GET", "POST"])
def edit_profile():
    if request.method == "POST":
        profile()
    else:
        return render_template('edit-profile.html')

@app.route('/sign-up', methods =["GET", "POST"])
def sign_up():
    if request.method == "POST":
        return render_template('dashboard.html')
    else:
        return render_template('sign-up.html')

def predict_price(valueDate, bondId, evalMidYield, compositeLiquidityScore, couponFrequency, nextCouponRate, modifiedDuration, evalMidPrice, rating, remainingTenure):
    data = {
        "data":
        [
            {
                'VALUE DATE': valueDate,
                'ID': bondId,
                'EVAL MID YIELD': evalMidYield,
                'COMPOSITE LIQUIDITY SCORE (T-1)': compositeLiquidityScore,
                'COUPON FREQUENCY': couponFrequency,
                'NEXT COUPON RATE': nextCouponRate,
                'CALLABLE/PUTTABLE': 0,
                'MODIFIED DURATION': modifiedDuration,
                'EVAL MID PRICE': evalMidPrice,
                'RATING': rating,
                'REMAINING TENURE': remainingTenure,
            },
        ],
    }

    body = str.encode(json.dumps(data))

    url = 'http://3651c164-cb36-45b1-a573-b0ea096c9953.southeastasia.azurecontainer.io/score'
    api_key = '' # Replace this with the API key for the web service
    headers = {'Content-Type':'application/json', 'Authorization':('Bearer '+ api_key)}

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        Dict = eval(result)
        return(Dict['forecast'][0])
    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))
        return "Error! Try Again"

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
