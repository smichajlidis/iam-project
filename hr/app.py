from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
from jose import jwt

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://hr:hr@postgres:5432/hr_db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret'

CLIENT_ID = "hr"
REDIRECT_URI = "http://hr.local/callback"

db = SQLAlchemy(app)

class Employee(db.Model):
    user_id = db.Column(db.String(20), primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_to = db.Column(db.DateTime)
    identity_status = db.Column(db.Boolean, default=True)
    business_role = db.Column(db.String(20))
    manager = db.Column(db.String(20))

    def __repr__(self):
        return '<Employee %r>' % self.id

with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    if "user" not in session:
        return redirect(url_for('login'))

    else:
        employees = Employee.query.order_by(Employee.user_id.asc()).all()
        return render_template('index.html', employees=employees)
    #    return jsonify(access_token=session["user"]["access_token"], id_token=session["user"]["access_token"])

@app.route('/login')
def login():
    auth_url = (
            f"http://iam.local/realms/iam-project/protocol/openid-connect/auth"
            f"?client_id={CLIENT_ID}"
            f"&redirect_uri={REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=openid"
        )
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get("code")
    if not code:
        return "Unable to receive authorization code", 400

    token_response = requests.post(
        f"http://keycloak:8080/realms/iam-project/protocol/openid-connect/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
        }
    )
    tokens = token_response.json()
    access_token = tokens.get("access_token")
    id_token = tokens.get("id_token")

    if not access_token or not id_token:
        return f"Unable to download token: {tokens}", 400

    payload_access_token = jwt.get_unverified_claims(access_token)
    payload_id_token = jwt.get_unverified_claims(id_token)

    session["user"] = {
        "name": payload_access_token.get("name"),
        "roles": payload_access_token.get("resource_access", {}).get("rms", {}).get("roles", []),
        "access_token": payload_access_token,
        "id_token": payload_id_token
    }

    return redirect('/')

@app.route('/create', methods=["GET", "POST"])
def create():

    if request.method == 'POST':

        valid_from = ""
        valid_from_str = request.form.get('valid_from')
        if not valid_from_str:
            valid_from = datetime.utcnow()
        else:
            valid_from = datetime.strptime(valid_from_str, '%Y-%m-%d')

        valid_to = ""
        valid_to_str = request.form.get('valid_to')
        if valid_to_str:
            valid_to = datetime.strptime(valid_to_str, '%Y-%m-%d')
        else:
            valid_to = datetime.strptime('9999-12-31', '%Y-%m-%d')
 

        identity_status = True if request.form.get('identity_status') else False

        new_employee = Employee(
            user_id = request.form['user_id'],
            first_name = request.form['first_name'],
            last_name = request.form['last_name'],
            valid_from = valid_from,
            valid_to = valid_to,
            identity_status = identity_status,
            business_role = request.form['business_role'],
            manager = request.form['manager'])
        
        try:
            db.session.add(new_employee)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding new employee'
        
    else:   
        return render_template('create.html')

@app.route('/change-status/<string:user_id>', methods=["GET", "POST"])
def update_status(user_id):
    
    employee_to_update = Employee.query.get_or_404(user_id)

    if request.method == 'POST':
        employee_to_update.identity_status = not employee_to_update.identity_status

    try:
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem changing status that employee'

@app.route('/update/<string:user_id>', methods=["GET", "POST"])
def update(user_id):

    employee = Employee.query.get_or_404(user_id)

    if request.method == 'POST': 

        valid_from = ""
        valid_from_str = request.form.get('valid_from')
        if not valid_from_str:
            valid_from = datetime.utcnow()
        else:
            valid_from = datetime.strptime(valid_from_str, '%Y-%m-%d')

        valid_to = ""
        valid_to_str = request.form.get('valid_to')
        if valid_to_str:
            valid_to = datetime.strptime(valid_to_str, '%Y-%m-%d')
        else:
            valid_to = datetime.strptime('9999-12-31', '%Y-%m-%d')
 
        identity_status = True if request.form.get('identity_status') else False

        employee.first_name = request.form['first_name']
        employee.last_name = request.form['last_name']
        employee.valid_to = valid_to
        employee.identity_status = identity_status
        employee.business_role = request.form['business_role']
        employee.manager = request.form['manager']
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating new employee'
        
    else:
        return render_template('update.html', employee=employee)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
