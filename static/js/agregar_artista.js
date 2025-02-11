document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('agregar-artista').addEventListener('click', function () {
        const select = document.getElementById('artista');
        const artistaId = select.value;
        const artistaNombre = select.options[select.selectedIndex].text;

        if (artistaId) {
            const tabla = document.getElementById('tabla-artistas').getElementsByTagName('tbody')[0];
            const nuevaFila = tabla.insertRow();

            nuevaFila.innerHTML = `
                <td>${artistaNombre}</td>
                <td>Género</td>
                <td><img src="https://via.placeholder.com/50" alt="Imagen Artista"></td>
                <td>
                    <button type="button" class="btn-editar" data-id="${artistaId}">Editar</button>
                    <button type="button" class="btn-eliminar">Eliminar</button>
                </td>
                <input type="hidden" name="artistas[]" value="${artistaId}">
            `;

            // Evento para eliminar
            nuevaFila.querySelector('.btn-eliminar').addEventListener('click', function () {
                if (confirm("¿Estás seguro de que quieres eliminar este artista?")) {
                    tabla.removeChild(nuevaFila);
                }
            });

            // Evento para redirigir a la página de edición
            nuevaFila.querySelector('.btn-editar').addEventListener('click', function () {
                const artistaId = this.getAttribute('data-id');
                window.location.href = `/editar-artista/${artistaId}`;
            });
        }
    });
});
