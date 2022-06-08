from flask import Flask, render_template, url_for, flash, request, redirect, jsonify
from flask_mysql_connector import MySQL
import shortuuid

# Inicializamos APP
app = Flask(__name__)

# EndPoint
endpoint = 'http://short.url'

# Conexión MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'SQL223010'
app.config['MYSQL_DATABASE'] = 'db_shortURL'

# Iniciamos la base de datos
mysql = MySQL(app)

# Ruta inicial
@app.route('/', methods=['GET'])
def inicio():
    try:
        return render_template('index.html'), 200
    except:
        return render_template('404.html'), 404
    
# Ruta para crear enlace corto y almacenar en la base de datos
@app.route('/crear_enlace_corto', methods=['POST'])
def crear_enlace_corto():
    try:
        if request.method == 'POST':
            # Capturamos la URL
            url = request.form['url']
            cursor = mysql.connection.cursor()
            
            # Ciclo para validar enlace corto que no se duplique
            while True:
                # Generamos el enlace corto
                enlaces_cortos = shortuuid.ShortUUID().random(length=7)
                # Consultamos a la base de datos si existe enlace corto
                cursor.execute(
                    "SELECT * FROM enlaces WHERE enlaces_cortos = BINARY %s", (enlaces_cortos,))
                
                if not cursor.fetchone():
                    break
                
            # Consultamos si en la base de datos existe URL
            cursor.execute(
                "SELECT enlaces_cortos FROM enlaces WHERE URL = BINARY %s", (url,))
            data = cursor.fetchone()
            if data:
                nuevo_enlace = endpoint + '/' + data[0]
                return jsonify(respuesta=nuevo_enlace)
                
            # Ingresamos en la base de datos la URL enviada
            cursor.execute(
                "INSERT INTO enlaces (url, enlaces_cortos) VALUES (%s,%s)", (url, enlaces_cortos))
            
            # Guardamos cambios en Base de Datos
            mysql.connection.commit()
            
            # Cerramos la conexión de la base de datos
            cursor.close()
            nuevo_enlace = endpoint + '/' + enlaces_cortos
            
            return jsonify(respuesta=nuevo_enlace)
        
    except:    
        return jsonify(respuesta='Error en petición'), 500
    
    @app.route('/<id>')
    def obtener_url(id):
        try:
            cursor = mysql.connection.cursor()
            
            # Buscamos en la base de datos la dirección URL
            cursor.execute(
                "SELECT URL FROM ENLACES WHERE ENLACES_CORTOS = BINARY %s", (id,))
            
            # Guardamos en variable el resultado
            data = cursor.fetchone()
            
            # Cerramos conexión a Base de Datos
            cursor.close()
            return jsonify(respuesta=data[0]), 200
        
        except:
            return jsonify(respuesta='Error en petición'), 500
        
#Corremos APP
if __name__ == "__main__":
    app.run(port=80, debug=True)