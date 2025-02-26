USE discoteca;

-- Tabla: Links de Discoteca
CREATE TABLE links (
    id_link INT AUTO_INCREMENT PRIMARY KEY, -- ID único generado automáticamente
    id_referencia INT NOT NULL, -- Enlaza con artistas u otras entidades
    nombre_referencia VARCHAR(25) NOT NULL,
    id_discoteca INT NOT NULL,
    FOREIGN KEY (id_discoteca) REFERENCES discoteca(id_discoteca) ON DELETE CASCADE
);

-- Tabla: Detalle Link
CREATE TABLE detalle_link (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY, -- Contador único para cada detalle
    id_link INT NOT NULL, -- Relación con links
    tipo_link VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255),
    portada BOOLEAN NOT NULL DEFAULT FALSE,
    url VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_link) REFERENCES links(id_link) ON DELETE CASCADE
);


