from flask import Flask, redirect, request, jsonify, session, url_for, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
from jose import jwt

app = Flask(__name__)
app.secret_key = "supersecret"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

CLIENT_ID = "admin-app"
REDIRECT_URI = "http://admin.iam.local/callback"

@app.route("/")
def index():
    auth_url = (
        f"http://iam.local/realms/test-realm/protocol/openid-connect/auth"
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
        f"http://keycloak:8080/realms/test-realm/protocol/openid-connect/token",
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

    roles = payload.get("realm_access", {}).get("roles", [])

    role = ""

    preferred_roles = ["edit", "display", "execute"]
    role = next((r for r in preferred_roles if r in roles), "lack of roles")

    user_info = {
        "username": payload.get("preferred_username"),
        "email": payload.get("email"),
        "name": payload.get("name"),
        "role": role
    }

    session["user"] = {
        "username": payload.get("preferred_username"),
        "roles": payload.get("realm_access", {}).get("roles", [])
    }

    return render_template("index.html", user=user_info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)