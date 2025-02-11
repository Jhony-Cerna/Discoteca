document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".btn-editar").forEach(function (boton) {
        boton.addEventListener("click", function () {
            const fila = this.closest("tr"); 
            const nombreEvento = fila.cells[0].innerText; 
            window.location.href = `/editar_evento/${encodeURIComponent(nombreEvento)}`;
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
