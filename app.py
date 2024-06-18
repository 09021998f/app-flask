from flask import Flask, request, render_template
from datetime import datetime
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import *

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        if not request.form['sucursal']:
            return render_template('index.html', sucursales = Sucursal.query.all())
        else:
            id = request.form['sucursal']
            print(id)
            return render_template('index.html', sucursales = Sucursal.query.all())
    else:
        return render_template('index.html', sucursales = Sucursal.query.all())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
