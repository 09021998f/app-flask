from flask import Flask, request, render_template
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import *

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':                                                    #   Espera a recibir una solicitud post
            id_sucursal = request.form['sucursal']                                  #   una vez recibila solicitud guarda el valor obtenido en id_sucursal
            if id_sucursal:                                                         #   Verifico si id_sucursal tiene un valor
                sucursal = Sucursal.query.filter_by(id=id_sucursal).first()         #   obtengo una instancia de Sucursal en la base de datos q conincida con id_sucursal
                return render_template('home_despachante.html', sucursal=sucursal)  #   Renderizo la pagina home_despachante cual tiene links de las funcionalidades de despachante
            else:                                                                   #   si no recibo ningun valor del formulario renderizo la pagina index.html
                return render_template('index.html', sucursales=Sucursal.query.all())
    else:
        return render_template('index.html', sucursales=Sucursal.query.all())       #   Al no recibir solicitud post renderiza la pagina

@app.route('/registrar_paquete/<int:sucursal>', methods = ['GET', 'POST'])
def registrar_paquete(sucursal):
    if request.method == 'POST':#   Espera a recibir una solicitud post, si se ejecuta signfica q el usuario a enviado un formulario para registrar
        if not request.form.get('peso') and request.form.get('nombre') and request.form.get():# validacion de todos los campos
            return render_template('registrar_paquete.html', sucursal= Sucursal.query.filter_by(id=sucursal).first(), msg = 'Todos los campos son obligatorios!')
        else:
            try:
                ultimo_envio = Paquete.query.order_by(Paquete.id.desc()).first() #obtengo el ultimo envio registrado desde la base de datos
                nuevo_nro_envio = ultimo_envio.numeroenvio + 20 #   incremento en 20 para generar un nuevo numero de envio
                nuevo_paquete = Paquete(numeroenvio = nuevo_nro_envio, peso = request.form.get('peso'), nomdestinatario = request.form.get('nombre'), dirdestinatario = request.form.get('dir'), entregado = False ,observaciones = ' ', idsucursal = request.form.get('userId'), idtransporte = 0, idrepartidor = 0 )
                db.session.add(nuevo_paquete)#  registro en la base de datos el nuevo paquete
                db.session.commit()# confirmo la transaccion en la base de datos
                return render_template('registrar_paquete.html', sucursal= Sucursal.query.filter_by(id=sucursal).first(), msg = 'Registro Exitoso!')
            except Exception as e:
                print(str(e))
                msg = 'Hubo un error al registrar el paquete'
                return render_template('registrar_paquete.html', sucursal= Sucursal.query.filter_by(id=sucursal).first(), msg = msg)
    else:#   renderiza la pagina en caso de no recibir ninguna peticion post
        return render_template('registrar_paquete.html', sucursal= Sucursal.query.filter_by(id=sucursal).first())

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
        
@app.route('/llegada_transporte/<int:sucursal>', methods = ['GET', 'POST'])
def llegada_transporte(sucursal):
    if request.method == 'POST':
        sucursal_acutal = Sucursal.query.filter_by(id = sucursal).first()
        trasnporte_elegido = request.form.get('transporte')
        transporte_actual = Transporte.query.filter_by(id = trasnporte_elegido).first()
        transporte_actual.fechahorallegada = datetime.now()
        db.session.commit()
        msg='Registo de llegada exitoso'
        return render_template('llegada_transporte.html', transportes = Transporte.query.all(), sucursal = sucursal_acutal, msg = msg)
    else:
        sucursal_acutal = Sucursal.query.filter_by(id = sucursal).first()
        return render_template('llegada_transporte.html', transportes = Transporte.query.all(), sucursal = sucursal_acutal)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
