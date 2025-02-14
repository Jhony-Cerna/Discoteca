document.addEventListener("DOMContentLoaded", function () {
    // Función para manejar la eliminación de artistas
    function manejarEliminacion(fila) {
        if (confirm("¿Estás seguro de que quieres eliminar este artista?")) {
            const tabla = fila.closest('tbody');
            tabla.removeChild(fila);
        }
    }

    // Función para manejar la edición de artistas
    function manejarEdicion(artistaId) {
        window.location.href = `/editar-artista/${artistaId}`;
    }

    // Agregar eventos a los botones "Eliminar" y "Editar" en la tabla existente
    document.querySelectorAll('#tabla-artistas .btn-eliminar').forEach(function (boton) {
        boton.addEventListener('click', function () {
            const fila = this.closest('tr');
            manejarEliminacion(fila);
        });
    });

    document.querySelectorAll('#tabla-artistas .btn-editar').forEach(function (boton) {
        boton.addEventListener('click', function () {
            const artistaId = this.getAttribute('data-id');
            manejarEdicion(artistaId);
        });
    });

    // Agregar eventos al botón "Agregar Artista" (si existe)
    const botonAgregar = document.getElementById('agregar-artista');
    if (botonAgregar) {
        botonAgregar.addEventListener('click', function () {
            const select = document.getElementById('artista');
            const artistaId = select.value;
            const artistaNombre = select.options[select.selectedIndex].text;

            if (artistaId) {
                // Obtener el género del artista desde el servidor
                fetch(`/obtener_genero_artista/${artistaId}`)
                    .then(response => response.json())
                    .then(data => {
                        const genero = data.genero;

                        const tabla = document.getElementById('tabla-artistas').getElementsByTagName('tbody')[0];
                        const nuevaFila = tabla.insertRow();

                        nuevaFila.innerHTML = `
                            <td>${artistaNombre}</td>
                            <td>${genero}</td>
                            <td><img src="https://via.placeholder.com/50" alt="Imagen Artista"></td>
                            <td>
                                <button type="button" class="btn-editar" data-id="${artistaId}">Editar</button>
                                <button type="button" class="btn-eliminar">Eliminar</button>
                            </td>
                            <input type="hidden" name="artistas[]" value="${artistaId}">
                        `;

                        // Agregar eventos a los nuevos botones
                        nuevaFila.querySelector('.btn-eliminar').addEventListener('click', function () {
                            manejarEliminacion(nuevaFila);
                        });

                        nuevaFila.querySelector('.btn-editar').addEventListener('click', function () {
                            const artistaId = this.getAttribute('data-id');
                            manejarEdicion(artistaId);
                        });
                    })
                    .catch(error => console.error('Error al obtener el género del artista:', error));
            }
        });
    }
});