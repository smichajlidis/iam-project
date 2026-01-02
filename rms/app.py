from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
from jose import jwt
from auth import checks

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://rms:rms@postgres:5432/rms_db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret'

CLIENT_ID = "rms"
REDIRECT_URI = "http://rms.local/callback"

db = SQLAlchemy(app)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requestor = db.Column(db.String(50), default="Unknown")
    content = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(15), default="Submitted")

    def __repr__(self):
        return '<Request %r>' % self.id

with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    if "user" not in session:
        return redirect(url_for('login'))
    
    elif request.method == 'POST':
        request_content = request.form['content']
        new_request = Request(content=request_content,
                              requestor=session['user']['name'])

        try:
            db.session.add(new_request)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your request'
    else:
        requests = Request.query.order_by(Request.date_created.asc()).all()
        return render_template('index.html', requests=requests)
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

@app.route("/callback")
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
        "subordinates": payload_id_token.get("subordinates", []),
        "access_token": payload_access_token,
        "id_token": payload_id_token
    }

    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    request_to_delete = Request.query.get_or_404(id)

    if not checks.can_delete(request_to_delete):
        return "Forbidden", 403

    try:
        db.session.delete(request_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that request'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    request_to_update = Request.query.get_or_404(id)

    if not checks.can_update(request_to_update):
        return "Forbidden", 403

    if request.method == 'POST':
        request_to_update.content = request.form['content']
    
        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your request'
    
    else:
        return render_template('update.html', request=request_to_update)

@app.route("/update-status/<int:id>", methods=["POST"])
def update_status(id):
    request_to_update = Request.query.get_or_404(id)

    if not (checks.can_change_status_support_scope(request_to_update) and checks.can_change_status_manager_scope(request_to_update)):
        return "Forbidden", 403

    request_to_update.status = request.form["status"]
    db.session.commit()
    return redirect("/")

@app.context_processor
def inject_auth_checks():
    return {
        "auth": checks
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
