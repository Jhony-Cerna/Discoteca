document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btn-editar").forEach(function (boton) {
        boton.addEventListener("click", function () {
            const fila = this.closest("tr");
            const nombreEvento = fila.cells[0].innerText; // Nombre del evento

            // Obtener los artistas asociados al evento
            fetch(`/obtener_artistas_evento/${encodeURIComponent(nombreEvento)}`)
                .then(response => response.json())
                .then(data => {
                    const artistas = data.artistas; // Lista de artistas
                    // Redirigir a la página de edición con los datos del evento y los artistas
                    window.location.href = `/editar_evento/${encodeURIComponent(nombreEvento)}?artistas=${encodeURIComponent(JSON.stringify(artistas))}`;
                })
                .catch(error => console.error('Error al obtener los artistas:', error));
        });
    });

    // Botón eliminar
    document.querySelectorAll(".btn-eliminar").forEach(function (boton) {
        boton.addEventListener("click", function () {
            const fila = this.closest("tr");
            const nombreEvento = fila.cells[0].innerText.trim();

            const confirmar = confirm(`¿Estás seguro de que deseas eliminar el evento "${nombreEvento}"?`);
            if (confirmar) {
                fetch(`/eliminar_evento/${encodeURIComponent(nombreEvento)}`, { method: "POST" })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            fila.remove();
                            alert("Evento eliminado correctamente.");
                        } else {
                            alert("Error al eliminar el evento.");
                        }
                    });
            }
        });
    });
});