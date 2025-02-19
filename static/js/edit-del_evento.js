document.addEventListener("DOMContentLoaded", function () {
    const urlParams = new URLSearchParams(window.location.search);
    const nombreEvento = urlParams.get("nombre_evento");

    if (nombreEvento) {
        fetch(`/obtener_artistas_evento/${encodeURIComponent(nombreEvento)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Error al obtener los artistas:", data.error);
                    return;
                }

                let tbody = document.querySelector("#tabla-artistas tbody");
                tbody.innerHTML = ""; // Limpiar antes de agregar

                data.artistas.forEach(artista => {
                    let row = document.createElement("tr");
                    row.innerHTML = `
                        <td>${artista.nombre}</td>
                        <td>${artista.genero}</td>
                        <td>
                            <button class="btn-editar" data-id="${artista.id_artista}">Editar</button>
                            <button class="btn-eliminar" onclick="eliminarArtista(${artista.id_artista})">Eliminar</button>
                        </td>
                        <input type="hidden" name="artistas[]" value="${artista.id_artista}">
                    `;
                    tbody.appendChild(row);
                });
            })
            .catch(error => console.error("Error al obtener los artistas:", error));
    }

    // Funcionalidad para eliminar eventos
    document.querySelectorAll(".btn-eliminar").forEach(button => {
        button.addEventListener("click", function () {
            const fila = this.closest("tr"); // Obtener la fila del evento
            const nombreEvento = fila.querySelector("td").textContent.trim(); // Obtener el nombre del evento

            if (confirm(`¿Seguro que quieres eliminar el evento "${nombreEvento}"?`)) {
                fetch(`/eliminar_evento/${encodeURIComponent(nombreEvento)}`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        fila.remove(); // Eliminar la fila de la tabla si el backend responde con éxito
                        alert("Evento eliminado correctamente.");
                    } else {
                        alert("Error al eliminar el evento: " + data.error);
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    alert("Hubo un problema al eliminar el evento.");
                });
            }
        });
    });
});

// Función para eliminar artistas (ya estaba en tu código)
function eliminarArtista(id_artista) {
    if (confirm("¿Seguro que quieres eliminar este artista?")) {
        fetch(`/eliminar_artista/${id_artista}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector(`[data-id='${id_artista}']`).closest("tr").remove();
            } else {
                alert("Error al eliminar el artista: " + data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    }
}
