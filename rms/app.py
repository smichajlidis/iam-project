from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['SQLALCHEMY_DATABASE_URI'] = ("postgresql://rms:rms@postgres:5432/rms_db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret'

db = SQLAlchemy(app)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Request %r>' % self.id

with app.app_context():
    db.create_all()

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        request_content = request.form['content']
        new_request = Request(content=request_content)

        try:
            db.session.add(new_request)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your request'
    else:
        requests = Request.query.order_by(Request.date_created.asc()).all()
        return render_template('index.html', requests=requests)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
