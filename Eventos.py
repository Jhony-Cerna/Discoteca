import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from urllib.parse import urlparse, urljoin
import json

app = Flask(__name__)

# MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'discoteca'
mysql = MySQL(app)

# Setting sessions
app.secret_key = 'mysecretkey'

@app.route('/', methods=['GET'])
def eventos_tabla():
    # Obtener los eventos de la base de datos
    cur = mysql.connection.cursor()
    cur.execute('SELECT nombre_evento, descripcion, fecha, lugar, hora FROM eventos')
    eventos = cur.fetchall()
    cur.close()

    # Renderizar la plantilla Eventos_Tabla.html con los eventos
    return render_template('Eventos_Tabla.html', eventos=eventos)

#agregar evento-----------
@app.route('/agregar_evento', methods=['GET', 'POST'])
def agregar_evento():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre_evento = request.form['nombre']
            descripcion = request.form['descripcion']
            lugar = request.form['direccion']
            fecha = request.form['fecha']
            hora = request.form['hora']
            artistas_seleccionados = json.loads(request.form['artistas'])  # Lista de IDs

            # Insertar evento
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO eventos 
                (nombre_evento, descripcion, lugar, fecha, hora, id_discoteca) 
                VALUES (%s, %s, %s, %s, %s, 1)
            """, (nombre_evento, descripcion, lugar, fecha, hora))
            
            id_evento = cur.lastrowid

            # Insertar relaciones
            for id_artista in artistas_seleccionados:
                cur.execute("""
                    INSERT INTO artistas_evento (id_evento, id_artista)
                    VALUES (%s, %s)
                """, (id_evento, id_artista))

            mysql.connection.commit()
            flash('Evento creado exitosamente', 'success')
            
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error: {str(e)}', 'danger')
        finally:
            cur.close()
        return redirect(url_for('eventos_tabla'))

    # GET: Mostrar formulario
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_artista, nombre FROM artistas")
    artistas = cur.fetchall()
    cur.close()
    
    return render_template('agregar_evento.html', artistas=artistas)



@app.route('/obtener_datos_artista/<int:id_artista>')
def obtener_datos_artista(id_artista):
    cur = mysql.connection.cursor()
    cur.execute("SELECT nombre, genero_musical FROM artistas WHERE id_artista = %s", (id_artista,))
    artista = cur.fetchone()
    cur.close()
    return jsonify({'nombre': artista[0], 'genero': artista[1]})



# Editar evento
@app.route('/editar_evento/<string:nombre_evento>', methods=['GET', 'POST'])
def editar_evento(nombre_evento):
    cur = mysql.connection.cursor()

    # Obtener datos del evento
    cur.execute("SELECT * FROM eventos WHERE nombre_evento = %s", (nombre_evento,))
    evento = cur.fetchone()

    if not evento:
        return "Evento no encontrado", 404

    # Obtener artistas
    cur.execute("SELECT * FROM artistas")
    artistas = cur.fetchall()

    # Obtener artistas asignados
    cur.execute("""
        SELECT a.id_artista, a.nombre, a.genero_musical 
        FROM artistas a 
        INNER JOIN artistas_evento ae ON a.id_artista = ae.id_artista 
        WHERE ae.id_evento = %s
    """, (evento[0],))
    artistas_asignados = cur.fetchall()

    if request.method == 'POST':
        # Actualizar datos del evento
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        direccion = request.form['direccion']
        fecha = request.form['fecha']
        hora = request.form['hora']
        nuevos_artistas = request.form.getlist('artistas[]')

        # Actualizar evento
        cur.execute('''
            UPDATE eventos SET 
            nombre_evento = %s, 
            descripcion = %s, 
            lugar = %s, 
            fecha = %s, 
            hora = %s 
            WHERE id_evento = %s
        ''', (nombre, descripcion, direccion, fecha, hora, evento[0]))
        
        # Sincronizar artistas
        artistas_actuales = [str(a[0]) for a in artistas_asignados]
        
        # Eliminar relaciones removidas
        for id_artista in artistas_actuales:
            if id_artista not in nuevos_artistas:
                cur.execute('''
                    DELETE FROM artistas_evento 
                    WHERE id_evento = %s AND id_artista = %s
                ''', (evento[0], id_artista))
        
        # Agregar nuevas relaciones
        for id_artista in nuevos_artistas:
            if id_artista not in artistas_actuales:
                cur.execute('''
                    INSERT INTO artistas_evento (id_evento, id_artista)
                    VALUES (%s, %s)
                ''', (evento[0], id_artista))
        
        mysql.connection.commit()
        return redirect(url_for('eventos_tabla'))  # Asegúrate de tener esta ruta definida

    return render_template('Actualizar_evento.html',
                        evento=evento,
                        artistas=artistas,
                        artistas_asignados=artistas_asignados)



# Nueva ruta para obtener artistas relacionados a un evento específico
@app.route('/obtener_artistas_evento/<string:nombre_evento>')
def obtener_artistas_evento(nombre_evento):
    cur = mysql.connection.cursor()

    # Obtener el ID del evento
    cur.execute('SELECT id_evento FROM eventos WHERE nombre_evento = %s', (nombre_evento,))
    resultado = cur.fetchone()

    if not resultado:
        return jsonify({'error': 'Evento no encontrado'}), 404

    id_evento = resultado[0]

    # Obtener artistas del evento
    cur.execute("""
        SELECT a.nombre 
        FROM artistas_evento ae
        JOIN artistas a ON ae.id_artista = a.id_artista
        WHERE ae.id_evento = %s
    """, (id_evento,))
    artistas = [artista[0] for artista in cur.fetchall()]

    cur.close()

    return jsonify({'artistas': artistas})


@app.route('/eliminar_evento/<nombre_evento>', methods=['POST'])
def eliminar_evento(nombre_evento):
    cur = mysql.connection.cursor()

    try:
        # Eliminar las relaciones en la tabla artistas_evento
        cur.execute('DELETE FROM artistas_evento WHERE id_evento = (SELECT id_evento FROM eventos WHERE nombre_evento = %s)', (nombre_evento,))
        
        # Eliminar el evento de la tabla eventos
        cur.execute('DELETE FROM eventos WHERE nombre_evento = %s', (nombre_evento,))
        
        mysql.connection.commit()
        cur.close()

        return jsonify({'success': True})
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({'success': False, 'error': str(e)})
    
#ARTISTAS
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

@app.route('/artistas', methods=['GET', 'POST'])
def artistas():
    next_url = request.args.get('next', '')
    form_data = request.form if request.method == 'POST' else None

    try:
        # Verificar y mantener conexión activa
        if not mysql.connection.open:
            mysql.connection.ping(reconnect=True)
            
        if request.method == 'POST':
            # Validación de campos obligatorios
            required_fields = ['nombreArtistico', 'generoMusical', 'descripcion']
            if not all(request.form.get(field) for field in required_fields):
                flash('Los campos marcados con * son obligatorios', 'danger')
                return render_template('artistas.html',
                                    next_url=next_url,
                                    form_data=request.form)

            try:
                cur = mysql.connection.cursor()
                
                # Consulta actualizada sin columna imagen
                cur.execute('''
                    INSERT INTO artistas 
                    (nombre, genero_musical, descripcion) 
                    VALUES (%s, %s, %s)
                ''', (
                    request.form['nombreArtistico'],
                    request.form['generoMusical'],
                    request.form['descripcion']
                ))
                
                mysql.connection.commit()
                flash('Artista registrado exitosamente', 'success')

                # Redirección segura
                safe_next_url = next_url if is_safe_url(next_url) else ''
                return redirect(safe_next_url) if safe_next_url else redirect(url_for('agregar_evento'))

            except Exception as e:
                mysql.connection.rollback()
                flash(f'Error al guardar el artista: {str(e)}', 'danger')
                return render_template('artistas.html',
                                    next_url=next_url,
                                    form_data=request.form)
            finally:
                if 'cur' in locals(): cur.close()

        # GET: Mostrar formulario
        safe_next = next_url if is_safe_url(next_url) else ''
        return render_template('artistas.html',
                            next_url=safe_next,
                            form_data=form_data)

    except Exception as e:
        flash(f'Error de conexión: {str(e)}', 'danger')
        mysql.connection.ping(reconnect=True)
        return redirect(request.url)

@app.route('/editar-artista/<int:id_artista>', methods=['GET', 'POST'])
def editar_artista(id_artista):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form.get('nombreArtistico')
        genero = request.form.get('generoMusical')
        descripcion = request.form.get('descripcion')

        # Actualizar el artista en la base de datos
        cur.execute(
            'UPDATE artistas SET nombre = %s, genero_musical = %s, descripcion = %s WHERE id_artista = %s',
            (nombre, genero, descripcion, id_artista)
        )
        mysql.connection.commit()

        # Obtener el parámetro de redirección
        redirect_to = request.args.get('redirect', 'agregar_evento')

        # Redirigir según el parámetro
        if redirect_to == 'editar_evento':
            nombre_evento = request.args.get('nombre_evento')  # Obtener el nombre del evento
            flash('Artista actualizado correctamente', 'success')
            return redirect(url_for('editar_evento', nombre_evento=nombre_evento))
        else:
            flash('Artista actualizado correctamente', 'success')
            return redirect(url_for('agregar_evento'))

    # Obtener datos actuales del artista
    cur.execute('SELECT nombre, genero_musical, descripcion FROM artistas WHERE id_artista = %s', (id_artista,))
    artista = cur.fetchone()
    cur.close()

    if not artista:
        flash('Artista no encontrado', 'danger')
        return redirect(url_for('agregar_evento'))

    return render_template('Actualizar_artista.html', artista=artista)


@app.route('/obtener_artistas', methods=['GET'])
def obtener_artistas():
    cur = mysql.connection.cursor()
    cur.execute('SELECT id_artista, nombre FROM artistas')
    artistas = cur.fetchall()
    cur.close()

    # Convertir los datos a formato JSON
    artistas_json = [{'id_artista': artista[0], 'nombre': artista[1]} for artista in artistas]
    return jsonify(artistas_json)


@app.route('/obtener_genero_artista/<int:id_artista>')
def obtener_genero_artista(id_artista):
    cur = mysql.connection.cursor()
    cur.execute("SELECT genero_musical FROM artistas WHERE id_artista = %s", (id_artista,))
    genero = cur.fetchone()[0]
    cur.close()
    return jsonify({'genero': genero})

    
if __name__ == '__main__':
    app.run(port=3000, debug=True)