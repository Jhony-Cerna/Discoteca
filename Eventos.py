import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL

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

@app.route('/agregar_evento', methods=['GET', 'POST'])
def agregar_evento():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_evento = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        lugar = request.form.get('direccion')
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')
        id_discoteca = 1  # Valor fijo según lo indicado

        # Obtener los artistas seleccionados
        artistas_seleccionados = request.form.getlist('artistas[]')

        # Insertar el evento en la tabla eventos
        cur = mysql.connection.cursor()
        cur.execute(
            'INSERT INTO eventos (nombre_evento, descripcion, lugar, fecha, hora, id_discoteca) VALUES (%s, %s, %s, %s, %s, %s)',
            (nombre_evento, descripcion, lugar, fecha, hora, id_discoteca)
        )
        mysql.connection.commit()

        # Obtener el id_evento recién creado
        id_evento = cur.lastrowid

        # Insertar las relaciones en la tabla artistas_evento
        for id_artista in artistas_seleccionados:
            cur.execute(
                'INSERT INTO artistas_evento (id_evento, id_artista) VALUES (%s, %s)',
                (id_evento, id_artista)
            )
        mysql.connection.commit()

        cur.close()
        flash('Evento y artistas guardados exitosamente', 'success')
        return redirect(url_for('eventos_tabla'))

    # Si es GET, mostrar el formulario
    artistas = session.get('artistas', [])
    if not artistas:
        cur = mysql.connection.cursor()
        cur.execute('SELECT id_artista, nombre FROM artistas')
        artistas = cur.fetchall()
        cur.close()
        session['artistas'] = artistas

    return render_template('agregar_evento.html', artistas=artistas)


@app.route('/editar_evento/<string:nombre_evento>', methods=['GET', 'POST'])
def editar_evento(nombre_evento):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nuevo_nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        lugar = request.form.get('direccion')  # Corregido a 'lugar'
        fecha = request.form.get('fecha')
        hora = request.form.get('hora')

        # ACTUALIZA LOS CAMPOS USANDO nombre_evento
        cur.execute(
            'UPDATE eventos SET nombre_evento = %s, descripcion = %s, lugar = %s, fecha = %s, hora = %s WHERE nombre_evento = %s',
            (nuevo_nombre, descripcion, lugar, fecha, hora, nombre_evento)
        )
        mysql.connection.commit()
        cur.close()

        flash('Evento actualizado correctamente', 'success')
        return redirect(url_for('eventos_tabla'))

    # OBTIENE LOS DATOS DEL EVENTO
    cur.execute('SELECT nombre_evento, descripcion, lugar, fecha, hora FROM eventos WHERE nombre_evento = %s', (nombre_evento,))
    evento = cur.fetchone()

    if not evento:
        flash('Evento no encontrado', 'danger')
        cur.close()
        return redirect(url_for('eventos_tabla'))

    # OBTIENE LOS ARTISTAS ASOCIADOS AL EVENTO (INCLUYENDO EL GÉNERO)
    cur.execute('''
        SELECT a.id_artista, a.nombre, a.genero_musical 
        FROM artistas a
        JOIN artistas_evento ae ON a.id_artista = ae.id_artista
        JOIN eventos e ON ae.id_evento = e.id_evento
        WHERE e.nombre_evento = %s
    ''', (nombre_evento,))
    artistas = cur.fetchall()

    cur.close()

    # PASA LOS DATOS DEL EVENTO Y LOS ARTISTAS A LA PLANTILLA
    return render_template('Actualizar_evento.html', evento=evento, artistas=artistas)



@app.route('/artistas', methods=['GET', 'POST'])
def artistas():
    if request.method == 'POST':
        nombre_artistico = request.form.get('nombreArtistico')
        genero_musical = request.form.get('generoMusical')
        descripcion = request.form.get('descripcion')

        # Validar que todos los campos estén presentes
        if not nombre_artistico or not genero_musical or not descripcion:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('artistas'))

        # Insertar en la base de datos
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                'INSERT INTO artistas (nombre, genero_musical, descripcion) VALUES (%s, %s, %s)',
                (nombre_artistico, genero_musical, descripcion)
            )
            mysql.connection.commit()
            flash('Artista agregado exitosamente', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al agregar el artista: {str(e)}', 'danger')
        finally:
            cur.close()

        # Obtener la lista actualizada de artistas
        cur = mysql.connection.cursor()
        cur.execute('SELECT id_artista, nombre FROM artistas')
        artistas = cur.fetchall()
        cur.close()

        # Guardar la lista de artistas en la sesión
        session['artistas'] = artistas

        # Redirigir a agregar_evento
        return redirect(url_for('agregar_evento'))

    return render_template('artistas.html')

@app.route('/editar-artista/<int:id_artista>', methods=['GET', 'POST'])
def editar_artista(id_artista):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nombre = request.form.get('nombreArtistico')
        genero = request.form.get('generoMusical')
        descripcion = request.form.get('descripcion')

        cur.execute(
            'UPDATE artistas SET nombre = %s, genero_musical = %s, descripcion = %s WHERE id_artista = %s',
            (nombre, genero, descripcion, id_artista)
        )
        mysql.connection.commit()

        # Recargar los artistas en la sesión
        cur.execute('SELECT id_artista, nombre FROM artistas')
        artistas = cur.fetchall()
        session['artistas'] = artistas

        cur.close()

        flash('Artista actualizado correctamente', 'success')
        return redirect(url_for('agregar_evento'))

    # Obtener datos actuales del artista
    cur.execute('SELECT nombre, genero_musical, descripcion FROM artistas WHERE id_artista = %s', (id_artista,))
    artista = cur.fetchone()
    cur.close()

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

@app.route('/obtener_genero_artista/<int:id_artista>', methods=['GET'])
def obtener_genero_artista(id_artista):
    cur = mysql.connection.cursor()
    cur.execute('SELECT genero_musical FROM artistas WHERE id_artista = %s', (id_artista,))
    genero = cur.fetchone()
    cur.close()

    if genero:
        return jsonify({'genero': genero[0]})
    else:
        return jsonify({'genero': 'Desconocido'})


if __name__ == '__main__':
    app.run(port=3000, debug=True)