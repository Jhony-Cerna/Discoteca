import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL

app = Flask(__name__)

#Mysql connection
app.config ['MYSQL_HOST'] = 'localhost'
app.config ['MYSQL_USER'] = 'root'
app.config ['MYSQL_PASSWORD'] = ''
app.config ['MYSQL_DB'] = 'discoteca'
mysql = MySQL(app)

#setting sesions
app.secret_key = 'mysecretkey'

@app.route('/')
def Index():
# Crear cursor y consultar la base de datos
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            p.id_producto,  -- Asegúrate de seleccionar id_producto como el primer campo
            p.tipo, 
            p.nombre, 
            p.descripcion, 
            p.precio_regular, 
            p.promocion, 
            e.capacidad, 
            e.contenido, 
            e.estado, 
            e.ubicacion,
            e.reserva
        FROM 
            productos p
        LEFT JOIN 
            espacios e
        ON 
            p.id_producto = e.id_producto
    """)
    data = cur.fetchall()  # Obtener todos los registros
    cur.close()

    # Renderizar el archivo HTML con los datos
    return render_template('index.html', productos=data)


#Definimos la ruta para las imagenes:
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Asegurar que la carpeta exista
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



@app.route('/filtrar/<tipo>')
def filtrar_por_tipo(tipo):
    cur = mysql.connection.cursor()

    # Consulta para obtener los productos filtrados por tipo
    cur.execute("""
        SELECT 
            p.id_producto, p.tipo, p.nombre, p.descripcion, p.precio_regular, p.promocion,
            e.capacidad, e.contenido, e.estado, e.ubicacion
        FROM 
            productos p
        LEFT JOIN 
            espacios e
        ON 
            p.id_producto = e.id_producto
        WHERE 
            p.tipo = %s
    """, (tipo,))
    productos_filtrados = cur.fetchall()

    cur.close()

    # Convertir los datos en un formato JSON
    productos_json = [
        {
            'id_producto': producto[0],
            'tipo': producto[1],
            'nombre': producto[2],
            'descripcion': producto[3],
            'precio_regular': producto[4],
            'promocion': producto[5],
            'capacidad': producto[6],
            'contenido': producto[7],
            'estado': 'Disponible' if producto[8] else 'Ocupado',
            'ubicacion': producto[9] if producto[9] else None
        }
        for producto in productos_filtrados
    ]

    return jsonify(productos_json)



@app.route('/add_mesasyboxes', methods=['GET', 'POST'])
def add_mesasyboxes():
    if request.method == 'POST':
        # Obtener datos del formulario
        tipo = request.form['tipo']
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion')  # Opcional
        precio_regular = request.form['precio_regular']
        promocion = True if 'promocion' in request.form else False
        reserva = float(request.form.get('reserva', 0.00))  # Nuevo campo

        # Insertar en la tabla productos
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO productos (tipo, nombre, descripcion, precio_regular, promocion)
            VALUES (%s, %s, %s, %s, %s)
        """, (tipo, nombre, descripcion, precio_regular, promocion))
        mysql.connection.commit()

        # Obtener el id_producto generado
        id_producto = cur.lastrowid

        # Manejar subida de imagen
        imagen = request.files['ubicacion']
        if imagen and imagen.filename != '':
            filename = secure_filename(imagen.filename)
            ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            imagen.save(ruta_imagen)
            ruta_bd = ruta_imagen
        else:
            ruta_bd = None

        # Si el tipo es 'box' o 'mesa', insertar también en la tabla espacios
        if tipo in ['box', 'mesa']:
            capacidad = request.form['capacidad']
            tamanio = request.form.get('tamanio')  # Opcional
            contenido = request.form.get('contenido')  # Opcional
            estado = request.form['estado']

            cur.execute("""
                INSERT INTO espacios (id_producto, capacidad, tamanio, contenido, estado, ubicacion, reserva)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_producto, capacidad, tamanio, contenido, estado, ruta_bd, reserva))
            mysql.connection.commit()

        flash('Producto agregado satisfactoriamente')
        return redirect(url_for('Index'))

    return render_template('Agregar_Box.html')


@app.route('/edit/<id>')
def get_mesasyboxes(id):
    cur = mysql.connection.cursor()

    # Obtener los datos de la tabla productos
    cur.execute("SELECT * FROM productos WHERE id_producto = %s", (id,))
    producto = cur.fetchone()

    # Obtener los datos de la tabla espacios (si corresponde)
    cur.execute("SELECT * FROM espacios WHERE id_producto = %s", (id,))
    espacio = cur.fetchone()

    # Normalizar la ruta de la imagen (si existe)
    if espacio and espacio[5]:  # espacio[5] es la columna 'ubicacion'
        espacio = list(espacio)  # Convertir tupla a lista para modificar
        espacio[5] = espacio[5].replace("\\", "/")  # Reemplazar barras invertidas
        espacio = tuple(espacio)  # Convertir de nuevo a tupla

    cur.close()

    return render_template('Actualizar_Box.html', producto=producto, espacio=espacio)



@app.route('/update', methods=['POST'])
def update_mesasyboxes():
    if request.method == 'POST':
        # Obtener datos del formulario
        id_producto = request.form['id']
        tipo = request.form['tipo']
        nombre = request.form['nombre']
        descripcion = request.form.get('descripcion')
        precio_regular = request.form['precio_regular']
        promocion = True if 'promocion' in request.form else False
        reserva = float(request.form.get('reserva', 0.00))  # Nuevo campo

        # Actualizar la tabla productos
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE productos
            SET tipo = %s, nombre = %s, descripcion = %s, precio_regular = %s, promocion = %s
            WHERE id_producto = %s
        """, (tipo, nombre, descripcion, precio_regular, promocion, id_producto))
        mysql.connection.commit()

        # Si el tipo es 'box' o 'mesa', actualizar también en espacios
        if tipo in ['box', 'mesa']:
            capacidad = request.form['capacidad']
            tamanio = request.form.get('tamanio')
            contenido = request.form.get('contenido')
            estado = request.form['estado'] 

            # Manejar la imagen
            imagen = request.files['ubicacion']
            if imagen and imagen.filename != '':
                filename = secure_filename(imagen.filename)
                ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagen.save(ruta_imagen)
                ruta_bd = ruta_imagen

                # Actualizar la ruta de la imagen en la base de datos
                cur.execute("""
                    UPDATE espacios
                    SET capacidad = %s, tamanio = %s, contenido = %s, estado = %s, ubicacion = %s, reserva = %s
                    WHERE id_producto = %s
                """, (capacidad, tamanio, contenido, estado, ruta_bd, reserva, id_producto))
            else:
                # Si no se sube una nueva imagen, mantener la imagen anterior
                cur.execute("""
                    UPDATE espacios
                    SET capacidad = %s, tamanio = %s, contenido = %s, estado = %s, reserva = %s
                    WHERE id_producto = %s
                """, (capacidad, tamanio, contenido, estado, reserva, id_producto))

            mysql.connection.commit()

        cur.close()

        flash('Producto actualizado exitosamente')
        return redirect(url_for('Index'))


@app.route('/delete_all', methods=['POST'])
def delete_all():
    try:
        # Cursor para interactuar con la base de datos
        cur = mysql.connection.cursor()

        # Eliminar primero los registros relacionados en la tabla 'espacios'
        cur.execute("DELETE FROM espacios")
        
        # Luego eliminar los registros de la tabla 'productos'
        cur.execute("DELETE FROM productos")

        # Confirmar los cambios
        mysql.connection.commit()

        # Mensaje de éxito
        flash('Todos los registros han sido eliminados satisfactoriamente', 'success')
    except Exception as e:
        # En caso de error
        mysql.connection.rollback()
        flash(f'Error al eliminar registros: {str(e)}', 'danger')
    finally:
        cur.close()

    # Redirigir de vuelta al índice
    return redirect(url_for('Index'))




@app.route('/delete/<int:id_producto>', methods=['GET', 'POST'])
def delete_producto(id_producto):
    try:
        cur = mysql.connection.cursor()

        # Elimina primero los registros de la tabla "espacios" relacionados con el producto
        cur.execute("DELETE FROM espacios WHERE id_producto = %s", (id_producto,))

        # Luego elimina el producto de la tabla "productos"
        cur.execute("DELETE FROM productos WHERE id_producto = %s", (id_producto,))
        mysql.connection.commit()

        flash('Producto eliminado satisfactoriamente')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Ocurrió un error: {str(e)}')

    return redirect(url_for('Index'))

if __name__ == '__main__':
    app.run(port= 3000, debug= True)
