function saveFormData() {
    const formData = {
        nombre: document.getElementById('nombre').value,
        descripcion: document.getElementById('descripcion').value,
        direccion: document.getElementById('direccion').value,
        fecha: document.getElementById('fecha').value,
        hora: document.getElementById('hora').value,
        artistas: []
    };

    const tableRows = document.querySelectorAll('#tabla-artistas tbody tr');
    tableRows.forEach(row => {
        const cells = row.querySelectorAll('td');
        formData.artistas.push({
            id: row.querySelector('input[name="artistas[]"]').value,
            nombre: cells[1].innerText,
            genero: cells[2].innerText,
            imagen: cells[3].innerText
        });
    });

    localStorage.setItem('formData', JSON.stringify(formData));
}

function updateArtistInLocalStorage(artistId, updatedArtist) {
    const savedData = JSON.parse(localStorage.getItem('formData'));
    if (savedData) {
        const artistIndex = savedData.artistas.findIndex(artista => artista.id === artistId);
        if (artistIndex !== -1) {
            savedData.artistas[artistIndex] = updatedArtist;
            localStorage.setItem('formData', JSON.stringify(savedData));
        }
    }
}

document.getElementById('crear-artista-link').addEventListener('click', (e) => {
    e.preventDefault();
    saveFormData();
    window.location.href = '/artistas';
});

window.addEventListener('load', () => {
    const savedData = JSON.parse(localStorage.getItem('formData'));
    if (savedData) {
        document.getElementById('nombre').value = savedData.nombre;
        document.getElementById('descripcion').value = savedData.descripcion;
        document.getElementById('direccion').value = savedData.direccion;
        document.getElementById('fecha').value = savedData.fecha;
        document.getElementById('hora').value = savedData.hora;

        const tbody = document.querySelector('#tabla-artistas tbody');
        savedData.artistas.forEach(artista => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${artista.id}</td>
                <td>${artista.nombre}</td>
                <td>${artista.genero}</td>
                <td>${artista.imagen}</td>
                <td>
                    <button type="button" class="btn-editar" data-id="${artista.id}">Editar</button>
                    <button type="button" class="btn-eliminar">Eliminar</button>
                </td>
                <input type="hidden" name="artistas[]" value="${artista.id}">
            `;
            row.querySelector('.btn-eliminar').addEventListener('click', function () {
                if (confirm('¿Estás seguro de que deseas eliminar este artista?')) {
                    const artistaId = row.querySelector('input[name="artistas[]"]').value;
                    let artistasIds = JSON.parse(localStorage.getItem('artistasIds')) || [];
                    artistasIds = artistasIds.filter(id => id !== artistaId);
                    localStorage.setItem('artistasIds', JSON.stringify(artistasIds));
                    row.remove();
                    saveFormData();
                }
            });

            row.querySelector('.btn-editar').addEventListener('click', function () {
                const artistaId = this.getAttribute('data-id');
                saveFormData();
                window.location.href = `/editar-artista/${artistaId}`;
            });

            tbody.appendChild(row);
        });
    }
});