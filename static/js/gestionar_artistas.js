document.addEventListener("DOMContentLoaded", () => {
    const tabla = document.querySelector("#tabla-artistas tbody");
    const selectArtista = document.getElementById("artista");
    const btnAgregar = document.getElementById("agregar-artista");

    // Delegación de eventos
    tabla.addEventListener("click", (e) => {
        const target = e.target;
        
        if (target.classList.contains("btn-eliminar")) {
            eliminarArtista(target);
        }
        
        if (target.classList.contains("btn-editar")) {
            editarArtista(target);
        }
    });

    // Agregar artista
    btnAgregar.addEventListener("click", async () => {
        const artistaId = selectArtista.value;
        const artistaNombre = selectArtista.options[selectArtista.selectedIndex].text;
        
        if (!artistaId || existeArtista(artistaId)) {
            alert(artistaId ? "Artista ya agregado" : "Seleccione un artista");
            return;
        }

        try {
            const response = await fetch(`/obtener_genero_artista/${artistaId}`);
            const data = await response.json();
            
            const nuevaFila = `
                <tr>
                    <td>${artistaNombre}</td>
                    <td>${data.genero}</td>
                    <td>
                        <button type="button" class="btn-editar" data-id="${artistaId}">Editar</button>
                        <button type="button" class="btn-eliminar" data-id="${artistaId}">Eliminar</button>
                    </td>
                    <input type="hidden" name="artistas[]" value="${artistaId}">
                </tr>
            `;
            
            tabla.insertAdjacentHTML('beforeend', nuevaFila);
        } catch (error) {
            console.error("Error al obtener género:", error);
        }
    });

    function existeArtista(id) {
        return Array.from(document.querySelectorAll('input[name="artistas[]"]'))
            .some(input => input.value === id);
    }

    function eliminarArtista(boton) {
        if (confirm("¿Eliminar artista de la lista?")) {
            const fila = boton.closest('tr');
            fila.remove();
        }
    }

    function editarArtista(boton) {
        const idArtista = boton.dataset.id;
        window.location.href = `/editar-artista/${idArtista}`;
    }
});