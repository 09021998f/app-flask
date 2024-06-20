from flask import Flask, request, render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import *

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
            id_sucursal = request.form['sucursal']  # Obtener el ID de sucursal desde el formulario
            if id_sucursal:  # Si se proporciona un ID de sucursal en el formulario
                sucursal = Sucursal.query.filter_by(id=id_sucursal).first()  # Obtener la sucursal por su ID
                if sucursal:
                    return render_template('home_despachante.html', sucursal=sucursal)
                else:
                    return 'No se encontró la sucursal.', 404  # Manejar caso de no encontrar la sucursal
            else:
                return render_template('index.html', sucursales=Sucursal.query.all())
    else:
        return render_template('index.html', sucursales=Sucursal.query.all())

@app.route('/registrar_paquete/<int:sucursal>', methods = ['GET', 'POST'])
def registrar_paquete(sucursal):
    if request.method == 'POST':
        id_sucursal = sucursal
        if not request.form.get('peso') and request.form.get('nombre') and request.form.get():
            return render_template('registrar_paquete.html', sucursal= Sucursal.query.filter_by(id=sucursal).first(), msg = 'Todos los campos son obligatorios!')
        else:
            try:
                ultimo_envio = Paquete.query.order_by(Paquete.id.desc()).first()
                nuevo_nro_envio = ultimo_envio.numeroenvio + 20
                nuevo_paquete = Paquete(numeroenvio = nuevo_nro_envio, peso = request.form.get('peso'), nomdestinatario = request.form.get('nombre'), dirdestinatario = request.form.get('dir'), entregado = False ,observaciones = ' ', idsucursal = request.form.get('userId'), idtransporte = 0, idrepartidor = 0 )
                
                db.session.add(nuevo_paquete)
                db.session.commit()
                return render_template('registrar_paquete.html', sucursal= Sucursal.query.filter_by(id=id_sucursal).first(), msg = 'Registro Exitoso!')
            except Exception as e:
                print(str(e))
                msg = f'Hubo un error al registrar el paquete'
                return render_template('registrar_paquete.html', sucursal= Sucursal.query.filter_by(id=id_sucursal).first(), msg = msg)
    else:
        id_sucursal = sucursal
        return render_template('registrar_paquete.html', sucursal= Sucursal.query.filter_by(id=id_sucursal).first())

@app.route('/solicitar_transporte/<int:sucursal>', methods=['GET', 'POST'])
def solicitar_transporte(sucursal):
    if request.method == 'POST':
        sucursal_destino = request.form.get('sucursal')
        paquetes_obt = Paquete.query.filter_by(idsucursal = sucursal).all()
        if paquetes_obt == []:
            return render_template('solicitar_transporte.html', sucursales = Sucursal.query.all(), msg = 'No hay paquetes en esta sucursal disponibles')
        return render_template('lista_paquetes.html', paquetes = paquetes_obt, sucursal = sucursal_destino)
    else:
        return render_template('solicitar_transporte.html', sucursales=Sucursal.query.all())


@app.route('/registrar_transporte', methods = ['GET', 'POST'])
def registrar_transporte():
    try:
        paquetes_obt = request.form.getlist('paquetes[]')
        sucursal_destino = request.form.get('sucId')
        print(sucursal_destino)
        ultimo_transporte = Transporte.query.order_by(Transporte.id.desc()).first()
        nuevo_nro_transporte = ultimo_transporte.numerotransporte + 1
        nuevo_transporte = Transporte(numerotransporte = nuevo_nro_transporte, fechahorasalida = datetime.now(), idsucursal = sucursal_destino)
        db.session.add(nuevo_transporte)
        db.session.commit()
        for paq in paquetes_obt:
            ultimo = Transporte.query.order_by(Transporte.id.desc()).first()
            paquete = Paquete.query.filter_by(id = paq).first()
            
            paquete.idtransporte = ultimo.id
            db.session.commit()
        return render_template('mensage.html', msg = 'Registro Exitoso!')
    except Exception as e:
        print(str(e))
        msg = f'Hubo un error al registrar el transporte'
        return render_template('lista_paquetes.html', paquetes = paquetes_obt, msg = msg)
        

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
