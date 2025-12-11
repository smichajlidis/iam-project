from flask import Flask, redirect, request
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

KEYCLOAK_URL = "http://iam.local/realms/test-realm/protocol/openid-connect/auth"
CLIENT_ID = "admin-app"
REDIRECT_URI = "http://admin.iam.local/callback"

@app.route("/")
def index():
    auth_url = (
	f"{KEYCLOAK_URL}"
	f"?client_id={CLIENT_ID}"
	f"&redirect_uri={REDIRECT_URI}"
	f"&response_type=code"
	f"&scope=openid"
    )
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    return f"Received code: {code}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
