from flask import Flask, render_template, url_for, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods =["GET", "POST"])
def dashboard():
    if request.method == "POST":
        call = request.form["call"]
        return render_template('dashboard.html', predicted_price=143) #testing purpose
    else:
        return render_template('dashboard.html')

@app.route('/recommendation')
def recommendation():
        return render_template('recommendation.html')
        
@app.route('/profile')
def profile():
        return render_template('profile.html')

@app.route('/upgrade')
def upgrade():
        return render_template('upgrade.html')

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)