-- Crear base de datos
CREATE DATABASE IF NOT EXISTS discoteca;
USE discoteca;

-- Tabla: Personas
CREATE TABLE IF NOT EXISTS personas (
    id_persona INT PRIMARY KEY, -- ID generado en el backend
    nombre VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50) NOT NULL,
    dni VARCHAR(8) UNIQUE NOT NULL,
    telefono VARCHAR(15),
    sexo ENUM('masculino', 'femenino'),
    fecha_nacimiento DATE NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    contrasenia VARCHAR(255) NOT NULL,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id_persona INT PRIMARY KEY,
    codigo_referido VARCHAR(20),
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona) ON DELETE CASCADE
);

-- Tabla: Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT PRIMARY KEY,
    id_persona INT NOT NULL,
    rol VARCHAR(25) NOT NULL,
    FOREIGN KEY (id_persona) REFERENCES personas(id_persona) ON DELETE CASCADE
);

-- Tabla: Discoteca
CREATE TABLE IF NOT EXISTS discoteca (
    id_discoteca INT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    direccion VARCHAR(255) NOT NULL,
    departamento VARCHAR(50) NOT NULL,
    provincia VARCHAR(50) NOT NULL,
    distrito VARCHAR(50) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    estado BOOLEAN NOT NULL DEFAULT FALSE,
    admin_id INT NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES usuarios(id_usuario)
);

-- Tabla: Información complementaria
CREATE TABLE IF NOT EXISTS info_complementaria (
    id_discoteca INT PRIMARY KEY,
    dias VARCHAR(50) DEFAULT 'No especificado',
    horario VARCHAR(50) DEFAULT 'No especificado',
    descripcion TEXT,
    generos_musica TEXT,
    ubicacion_latitud DECIMAL(10, 9) NOT NULL,
    ubicacion_longitud DECIMAL(10, 9) NOT NULL,
    FOREIGN KEY (id_discoteca) REFERENCES discoteca(id_discoteca) ON DELETE CASCADE
);

-- Tabla: Servicios Complementarios
CREATE TABLE IF NOT EXISTS servicios (
    id_servicio INT PRIMARY KEY,
    nombre_servicio VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    id_discoteca INT NOT NULL,
    FOREIGN KEY (id_discoteca) REFERENCES discoteca(id_discoteca) ON DELETE CASCADE
);

-- Tabla: Links de Discoteca
CREATE TABLE IF NOT EXISTS links (
    id_referencia INT PRIMARY KEY,
    nombre_referencia VARCHAR(25) NOT NULL,
    id_discoteca INT NOT NULL,
    FOREIGN KEY (id_discoteca) REFERENCES discoteca(id_discoteca) ON DELETE CASCADE
);

-- Tabla: Detalle Link
CREATE TABLE IF NOT EXISTS detalle_link (
    id_link INT,
    tipo_link VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    portada BOOLEAN NOT NULL DEFAULT FALSE,
    url VARCHAR(255) NOT NULL,
    id_referencia INT NOT NULL,
    PRIMARY KEY (id_link, id_referencia),
    FOREIGN KEY (id_referencia) REFERENCES links(id_referencia) ON DELETE CASCADE
);

-- Tabla: Eventos
CREATE TABLE IF NOT EXISTS eventos (
    id_evento INT PRIMARY KEY,
    id_discoteca INT NOT NULL,
    nombre_evento VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255),
    lugar VARCHAR(150) NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    precio DECIMAL(10, 2),
    FOREIGN KEY (id_discoteca) REFERENCES discoteca(id_discoteca) ON DELETE CASCADE
);

-- Tabla: Artistas
CREATE TABLE IF NOT EXISTS artistas (
    id_artista INT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    genero_musical VARCHAR(50),
    descripcion VARCHAR(255)
);

-- Tabla: Artistas del Evento
CREATE TABLE IF NOT EXISTS artistas_evento (
    id_evento INT NOT NULL,
    id_artista INT NOT NULL,
    PRIMARY KEY (id_evento, id_artista),
    FOREIGN KEY (id_evento) REFERENCES eventos(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_artista) REFERENCES artistas(id_artista) ON DELETE CASCADE
);

-- Tabla: Categorías de Bebidas
CREATE TABLE IF NOT EXISTS categoria_bebidas (
    id_categoria INT PRIMARY KEY,
    nombre_categoria VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255)
);

-- Tabla: Productos (supertipo)
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    tipo ENUM('box', 'mesa', 'bebida', 'piqueo', 'coctel') NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    precio_regular DECIMAL(10, 2) NOT NULL,
    promocion BOOLEAN NOT NULL DEFAULT FALSE
);

-- Tabla: Espacios (subtipo)
CREATE TABLE IF NOT EXISTS espacios (
    id_producto INT PRIMARY KEY,
    capacidad INT NOT NULL,
    tamanio VARCHAR(50),
    contenido TEXT,
    estado BOOLEAN NOT NULL DEFAULT TRUE,
    ubicacion VARCHAR(255),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

-- Tabla: Bebidas (subtipo)
CREATE TABLE IF NOT EXISTS bebidas (
    id_producto INT PRIMARY KEY,
    marca VARCHAR(50),
    tamanio DECIMAL(10, 2),
    stock INT DEFAULT 0,
    id_categoria INT,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categoria_bebidas(id_categoria) ON DELETE SET NULL
);

-- Tabla: Piqueos y Cocteles (subtipo)
CREATE TABLE IF NOT EXISTS piqueos_cocteles (
    id_producto INT PRIMARY KEY,
    tamanio VARCHAR(50),
    insumos TEXT,
    stock INT DEFAULT 0,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

-- Tabla: Promociones y Ofertas
CREATE TABLE IF NOT EXISTS promociones (
    id_promocion INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT,
    nombre VARCHAR(255),
    descripcion TEXT,
    porcentaje_descuento DECIMAL(5, 2) DEFAULT NULL,
    cantidad_comprar INT DEFAULT NULL,
    cantidad_pagar INT DEFAULT NULL,
    precio_fijo DECIMAL(10, 2) DEFAULT NULL,
    tipo_promocion ENUM('descuento', '2x1', 'precio_fijo') NOT NULL,
    fecha_inicio DATE,
    fecha_fin DATE,
    id_usuario INT,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Tabla: Auditoría de Productos
CREATE TABLE IF NOT EXISTS auditoria_productos (
    id_auditoria INT PRIMARY KEY,
    id_producto INT NOT NULL,
    campo_modificado VARCHAR(50) NOT NULL,
    valor_anterior DECIMAL(10, 2) NOT NULL,
    valor_nuevo DECIMAL(10, 2) NOT NULL,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL,
    motivo VARCHAR(255),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
);

-- Tabla: Carritos
CREATE TABLE IF NOT EXISTS carritos (
    id_carrito INT PRIMARY KEY,
    id_cliente INT NOT NULL,
    estado ENUM('activo', 'completado', 'abandonado') DEFAULT 'activo',
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_persona) ON DELETE CASCADE
);

-- Tabla: Detalles del Carrito
CREATE TABLE IF NOT EXISTS detalle_carrito (
    id_carrito INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_carrito, id_producto),
    FOREIGN KEY (id_carrito) REFERENCES carritos(id_carrito) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

-- Tabla: Pedidos
CREATE TABLE IF NOT EXISTS pedidos (
    id_pedido INT PRIMARY KEY,
    id_cliente INT NOT NULL,
    estado ENUM('pendiente', 'pagado', 'cancelado') DEFAULT 'pendiente',
    precio_total DECIMAL(10, 2),
    fecha_pedido DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_persona)
);

-- Tabla: Detalle de Pedido
CREATE TABLE IF NOT EXISTS detalle_pedido (
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    tipo_compra ENUM('venta', 'reserva') NOT NULL DEFAULT 'venta',
    precio_unitario DECIMAL(10, 2) NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    PRIMARY KEY (id_pedido, id_producto),
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Tabla: Pagos
CREATE TABLE IF NOT EXISTS pagos (
    id_pago INT PRIMARY KEY,
    id_pedido INT NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    metodo_pago ENUM('efectivo', 'tarjeta', 'transferencia') NOT NULL,
    fecha_pago DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_pedido) REFERENCES pedidos(id_pedido)
);

-- Tabla: Comprobantes de Pago
CREATE TABLE IF NOT EXISTS comprobantes_pago (
    id_pago INT PRIMARY KEY,
    tipo_comprobante ENUM('boleta', 'factura') NOT NULL,
    numero_serie VARCHAR(10) NOT NULL,
    numero_correlativo INT NOT NULL,
    razon_social VARCHAR(150),
    ruc VARCHAR(11),
    fecha_emision DATETIME DEFAULT CURRENT_TIMESTAMP,
    igv DECIMAL(10, 2),
    monto_total DECIMAL(10, 2) NOT NULL,
    estado ENUM('emitido', 'anulado') DEFAULT 'emitido',
    FOREIGN KEY (id_pago) REFERENCES pagos(id_pago),
    UNIQUE (numero_serie, numero_correlativo)
);

-- Tabla: Criterios de Calificación
CREATE TABLE IF NOT EXISTS criterios_calificacion (
    id_criterio INT PRIMARY KEY,
    nombre_criterio VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255)
);

-- Tabla: Calificaciones
CREATE TABLE IF NOT EXISTS calificaciones (
    id_cliente INT NOT NULL,
    id_criterio INT NOT NULL,
    calificacion INT NOT NULL,
    comentario TEXT,
    fecha_calificacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_cliente, id_criterio),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_persona) ON DELETE CASCADE,
    FOREIGN KEY (id_criterio) REFERENCES criterios_calificacion(id_criterio) ON DELETE CASCADE
);

-- Tabla: Favoritos
CREATE TABLE IF NOT EXISTS favoritos (
    id_cliente INT NOT NULL,
    id_producto INT NOT NULL,
    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_cliente, id_producto),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_persona) ON DELETE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto) ON DELETE CASCADE
);

-- Tabla: Sugerencias
CREATE TABLE IF NOT EXISTS sugerencias (
    id_cliente INT NOT NULL,
    id_criterio INT NOT NULL,
    sugerencia TEXT NOT NULL,
    fecha_sugerencia DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_cliente, id_criterio),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_persona) ON DELETE CASCADE,
    FOREIGN KEY (id_criterio) REFERENCES criterios_calificacion(id_criterio) ON DELETE CASCADE
);

-- Tabla: Reconocimientos
CREATE TABLE IF NOT EXISTS reconocimientos (
    id_cliente INT NOT NULL,
    id_criterio INT NOT NULL,
    contenido TEXT NOT NULL,
    fecha_reconocimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_cliente, id_criterio),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_persona) ON DELETE CASCADE,
    FOREIGN KEY (id_criterio) REFERENCES criterios_calificacion(id_criterio) ON DELETE CASCADE
);