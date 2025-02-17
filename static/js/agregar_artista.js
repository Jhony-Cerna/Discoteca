document.addEventListener("DOMContentLoaded", function () {
    // Función para manejar la eliminación de artistas
    function manejarEliminacion(fila) {
        if (confirm("¿Estás seguro de que quieres eliminar este artista?")) {
            const artistaId = fila.querySelector('input[name="artistas[]"]').value;
            let artistasIds = JSON.parse(localStorage.getItem('artistasIds')) || [];
            artistasIds = artistasIds.filter(id => id !== artistaId);
            localStorage.setItem('artistasIds', JSON.stringify(artistasIds));

            const tabla = fila.closest('tbody');
            tabla.removeChild(fila);
        }
    }

    // Función para manejar la edición de artistas
    function manejarEdicion(artistaId) {
        window.location.href = `/editar-artista/${artistaId}`;
    }

    // Agregar eventos a los botones "Eliminar" y "Editar" en la tabla existente
    function agregarEventosBotones() {
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
    }

    agregarEventosBotones();

    // Agregar eventos al botón "Agregar Artista" (si existe)
    const botonAgregar = document.getElementById('agregar-artista');
    if (botonAgregar) {
        botonAgregar.addEventListener('click', function () {
            const select = document.getElementById('artista');
            const artistaId = select.value;
            const artistaNombre = select.options[select.selectedIndex].text;

            if (artistaId) {
                // Verificar si el artista ya está en la tabla
                const existingRow = document.querySelector(`#tabla-artistas input[value="${artistaId}"]`);
                if (existingRow) {
                    alert('Este artista ya ha sido agregado.');
                    return;
                }

                // Obtener el género del artista desde el servidor
                fetch(`/obtener_genero_artista/${artistaId}`)
                    .then(response => response.json())
                    .then(data => {
                        const genero = data.genero;

                        const tabla = document.getElementById('tabla-artistas').getElementsByTagName('tbody')[0];
                        const nuevaFila = tabla.insertRow();

                        nuevaFila.innerHTML = `
                            <td>${artistaId}</td>
                            <td>${artistaNombre}</td>
                            <td>${genero}</td>
                            <td><img src="https://via.placeholder.com/50" alt="Imagen Artista"></td>
                            <td>
                                <button type="button" class="btn-editar" data-id="${artistaId}">Editar</button>
                                <button type="button" class="btn-eliminar">Eliminar</button>
                            </td>
                            <input type="hidden" name="artistas[]" value="${artistaId}">
                        `;

                        // Guardar el ID del artista en el local storage
                        let artistasIds = JSON.parse(localStorage.getItem('artistasIds')) || [];
                        if (!artistasIds.includes(artistaId)) {
                            artistasIds.push(artistaId);
                            localStorage.setItem('artistasIds', JSON.stringify(artistasIds));
                        }

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

    // Agregar artistas del local storage al formulario al enviar
    const form = document.querySelector('form');
    form.addEventListener('submit', function () {
        const artistasIds = JSON.parse(localStorage.getItem('artistasIds')) || [];
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'artistas';
        hiddenInput.value = JSON.stringify(artistasIds);
        form.appendChild(hiddenInput);
    });
});