document.addEventListener("DOMContentLoaded", () => {
    const localStorageKey = "artistasSeleccionados";
    const tabla = document.querySelector("#tabla-artistas tbody");
    const campoOculto = document.getElementById("artistas-seleccionados");

    // Cargar selecciones previas
    cargarSeleccionesPrevias();

    // Manejar agregar artista
    document.getElementById("agregar-artista").addEventListener("click", agregarArtista);

    // Manejar envío del formulario
    document.querySelector("form").addEventListener("submit", limpiarAlmacenamiento);

    function agregarArtista() {
        const select = document.getElementById("artista");
        const artistaId = select.value;
        const artistaNombre = select.options[select.selectedIndex].text;

        if (!artistaId || artistaYaAgregado(artistaId)) {
            alert(artistaId ? "Artista ya agregado" : "Seleccione un artista");
            return;
        }

        fetch(`/obtener_genero_artista/${artistaId}`)
            .then(response => response.json())
            .then(data => {
                crearFilaTabla(artistaId, artistaNombre, data.genero);
                guardarEnStorage(artistaId);
                actualizarCampoOculto();
            })
            .catch(error => console.error("Error:", error));
    }

    function artistaYaAgregado(id) {
        const ids = JSON.parse(localStorage.getItem(localStorageKey) || "[]");
        return ids.includes(id);
    }

    function crearFilaTabla(id, nombre, genero) {
        const fila = tabla.insertRow();
        fila.innerHTML = `
            <td>${nombre}</td>
            <td>${genero}</td>
            <td>
                <button type="button" class="btn-editar" data-id="${id}">Editar</button>
                <button type="button" class="btn-eliminar">Eliminar</button>
            </td>
        `;

        fila.querySelector(".btn-eliminar").addEventListener("click", () => {
            eliminarArtista(id, fila);
        });

        fila.querySelector(".btn-editar").addEventListener("click", () => {
            editarArtista(id);
        });
    }

    function eliminarArtista(id, fila) {
        const ids = JSON.parse(localStorage.getItem(localStorageKey) || "[]");
        const nuevosIds = ids.filter(artistaId => artistaId !== id);
        
        localStorage.setItem(localStorageKey, JSON.stringify(nuevosIds));
        fila.remove();
        actualizarCampoOculto();
    }

    function editarArtista(id) {
        window.location.href = `/editar-artista/${id}`;
    }

    function guardarEnStorage(id) {
        const ids = JSON.parse(localStorage.getItem(localStorageKey) || "[]");
        ids.push(id);
        localStorage.setItem(localStorageKey, JSON.stringify(ids));
    }

    function cargarSeleccionesPrevias() {
        const ids = JSON.parse(localStorage.getItem(localStorageKey) || "[]");
        ids.forEach(id => {
            fetch(`/obtener_datos_artista/${id}`)
                .then(response => response.json())
                .then(data => crearFilaTabla(id, data.nombre, data.genero));
        });
        actualizarCampoOculto();
    }

    function actualizarCampoOculto() {
        const ids = JSON.parse(localStorage.getItem(localStorageKey) || "[]");
        campoOculto.value = JSON.stringify(ids);
    }

    function limpiarAlmacenamiento() {
        localStorage.removeItem(localStorageKey);
    }
});
