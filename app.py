from flask import Flask, request, render_template
from datetime import datetime


"""
Crea una instancia de la aplicación Flask. __name__ es una variable especial de Python que representa 
el nombre del módulo en el que se encuentra el código actual. Cuando se pasa __name__, Flask utiliza 
esta información para localizar recursos (como plantillas y archivos estáticos).

"""
app = Flask(__name__)
app.config.from_pyfile('config.py')
"""
carga configuraciones desde un archivo Python específico (config.py) y las aplica a la aplicación Flask, 
permitiendo una configuración centralizada y flexible de la aplicación.
"""

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
        sucursal_destino = request.form.get('sucursal') #obtengo el id de la sucursal de destino 
        paquetes_obt = Paquete.query.filter_by(idsucursal = sucursal).all() # filtro los paquetes que son de la sucursal en la q trabaja el despachante
        if paquetes_obt == []: #si no hay paquetes renderizo la pagina otra vez con el alerta de msg
            return render_template('solicitar_transporte.html', sucursales = Sucursal.query.all(), msg = 'No hay paquetes en esta sucursal disponibles')
        return render_template('lista_paquetes.html', paquetes = paquetes_obt, sucursal = sucursal_destino) # muestro los paquetes obtenidos
    else:
        return render_template('solicitar_transporte.html', sucursales=Sucursal.query.all())


@app.route('/registrar_transporte', methods = ['GET', 'POST'])
def registrar_transporte(): # atravez del formulario de lista_paquetes envio los datos a esta funcion
    try:
        # Lista q contiene los paquetes seleccionados desde el checkbox del formulario
        paquetes_obt = request.form.getlist('paquetes[]') 
        # id de sucursal de destino
        sucursal_destino = request.form.get('sucId') 
        # obtener el ultimo transporte para generar un nuevo numero de transporte
        ultimo_transporte = Transporte.query.order_by(Transporte.id.desc()).first()
        nuevo_nro_transporte = ultimo_transporte.numerotransporte + 1
        # Creo un nuevo objeto en Transporte y guardo en la base de datos
        nuevo_transporte = Transporte(numerotransporte = nuevo_nro_transporte, fechahorasalida = datetime.now(), idsucursal = sucursal_destino)
        db.session.add(nuevo_transporte)
        db.session.commit()
        #P or cada paquete obtenido actualizo el id de transporte a los paquetes
        for paq in paquetes_obt:
            ultimo = Transporte.query.order_by(Transporte.id.desc()).first()
            paquete = Paquete.query.filter_by(id = paq).first()
            paquete.idtransporte = ultimo.id
            db.session.commit()
        # Renderiza la pagina en caso del q el registro sea exitoso
        return render_template('mensage.html', msg = 'Registro Exitoso!')
    except Exception as e:
        #manejo del error en el caso de que el registro haya realizado un error
        print(str(e)) #imprimo en consola el error para depuracion
        msg = f'Hubo un error al registrar el transporte'
        return render_template('lista_paquetes.html', paquetes = paquetes_obt, msg = msg)
        
@app.route('/llegada_transporte/<int:sucursal>', methods = ['GET', 'POST'])
def llegada_transporte(sucursal):
    if request.method == 'POST': #  En caso de que se reciba la solicitud post
        #   obntengo la sucursal en la cuale sta trabajando el despachante
        sucursal_acutal = Sucursal.query.filter_by(id = sucursal).first()
        #   guardo en la variable el numero de transporte elegido
        trasnporte_elegido = request.form.get('transporte')
        # Actualizacion de la fecha y hora de llegada del transporte
        transporte_actual = Transporte.query.filter_by(id = trasnporte_elegido).first()
        transporte_actual.fechahorallegada = datetime.now()
        db.session.commit()
        msg='Registo de llegada exitoso'
        return render_template('llegada_transporte.html', transportes = Transporte.query.all(), sucursal = sucursal_acutal, msg = msg)
    else:
        #   obntengo la sucursal en la cuale sta trabajando el despachante
        sucursal_acutal = Sucursal.query.filter_by(id = sucursal).first()
        return render_template('llegada_transporte.html', transportes = Transporte.query.all(), sucursal = sucursal_acutal)


if __name__ == '__main__':
    """
    app.app_context() crea un contexto de aplicación para la instancia de la aplicación Flask (app).
    Esto es necesario para que Flask y sus extensiones funcionen correctamente fuera del contexto 
    de una solicitud HTTP típica. Dentro de este contexto, puedes interactuar con la aplicación y 
    sus extensiones como si estuvieras manejando una solicitud real.
    
    """
    with app.app_context():
        """
        db.create_all() es un método de SQLAlchemy que crea todas las tablas definidas por tus modelos 
        SQLAlchemy. Esta operación crea las tablas en la base de datos si no existen. 
        Es importante ejecutar create_all() después de haber configurado los modelos SQLAlchemy.
        """
        db.create_all()
    app.run(debug=True)
    """
    inicia el servidor de desarrollo de Flask. Cuando debug=True está habilitado, Flask se ejecuta 
    en modo de depuración, lo que proporciona mensajes detallados de depuración en caso de errores 
    y reinicia automáticamente el servidor cuando detecta cambios en el código.
    """