import urllib.request
import json
import os
import ssl

# def allowSelfSignedHttps(allowed):
#     # bypass the server certificate verification on client side
#     if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
#         ssl._create_default_https_context = ssl._create_unverified_context

# allowSelfSignedHttps(True) # this line is needed if you use self-signed certificate in your scoring service.

# Request data goes here
data = {
    "data":
    [
        {
            'VALUE DATE': "2021-01-01-T00:00:000Z",
            'ID': "1",
            'EVAL MID YIELD': 3.772,
            'COMPOSITE LIQUIDITY SCORE (T-1)': "2.3",
            'COUPON FREQUENCY': "2",
            'NEXT COUPON RATE': "5.17",
            'CALLABLE/PUTTABLE': 0,
            'MODIFIED DURATION': "1.299",
            'EVAL MID PRICE': "101.832",
            'RATING': "2",
            'REMAINING TENURE': "3",
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
    print(Dict['forecast'][0])

    
except urllib.error.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(json.loads(error.read().decode("utf8", 'ignore')))


