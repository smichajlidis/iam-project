from flask import Flask

admin_bp = Flask(__name__)

@app.route("/")
def index():
    return "IAM Admin Panel — backend is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
