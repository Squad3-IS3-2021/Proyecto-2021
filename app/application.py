from flask import Flask, request, jsonify
import pycronofy


app = Flask(__name__)
app.config["DEBUG"] = True



@app.route('/', methods=['GET'])
def home():
    return jsonify(
        message='hello-world'
    )

@app.route('/testURL', methods=['GET'])
def testURL():
    # Initial authorization, needs cleanup and a better implementation:
    cronofy = pycronofy.Client(client_id='_EnkRaQwvl4aI9_5892h_AIUtI2TpvJ_', client_secret='tZDDBnlupQbP_seiAj2ccuTCIxvEhvKFLMgC1NDnLxNYF94hNdMsg-_an1VqsFSXTE1TlSnktDzOr7zfbD3jXA')

    url = cronofy.user_auth_link('http://localhost:5000/')
    print(url)
    print('Go to this url in your browser, and paste the code below')

    code = input('Paste Code Here: ') # raw_input() for python 2.
    auth = cronofy.get_authorization_from_code(code)
    return jsonify(
        message='hello-world'
    )
    

if __name__ == "__main__":
    app.run()