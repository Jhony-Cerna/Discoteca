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
            nombre: cells[0].innerText,
            genero: cells[1].innerText,
            imagen: cells[2].innerText
        });
    });

    localStorage.setItem('formData', JSON.stringify(formData));
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
                <td data-id="${artista.id}">${artista.nombre}</td>
                <td>${artista.genero}</td>
                <td>${artista.imagen}</td>
                <td>
                    <button type="button" class="btn-editar">Editar</button>
                    <button type="button" class="btn-eliminar">Eliminar</button>
                </td>
            `;
            row.querySelector('.btn-eliminar').addEventListener('click', function () {
                confirm('¿Estás seguro de que deseas eliminar este artista?');
                row.remove();
                saveFormData();
            });

            tbody.appendChild(row);
        });
    }
});