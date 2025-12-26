from flask import Flask, render_template, request, redirect, jsonify, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
from jose import jwt

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

    if not access_token:
        return f"Unable to download token: {tokens}", 400

    payload = jwt.get_unverified_claims(access_token)

    session["user"] = {
        "name": payload.get("name"),
        "roles": payload.get("realm_access", {}).get("roles", [])
    }

    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    request_to_delete = Request.query.get_or_404(id)

    try:
        db.session.delete(request_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that request'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    request_to_update = Request.query.get_or_404(id)

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
    request_to_update.status = request.form["status"]
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
