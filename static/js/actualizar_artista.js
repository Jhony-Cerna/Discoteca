function actualizar() {
    
    //obtener los datos guardardaos en el local storage
    const formData = JSON.parse(localStorage.getItem('formData'));
    //mostrar los datos del localstorage en un alert
    //alert(JSON.stringify(formData));
    //obtener los datos del formulario
    const nombre = document.getElementById('nombreArtistico').value;
    const generoMusical = document.getElementById('generoMusical').value;
    const descripcion = document.getElementById('descripcion').value;
    
    const url = window.location.href;
    const urlParts = url.split('/');
    const id = urlParts[urlParts.length - 1];
    //alert('Id del artista: ' + id);

    //buscar id en el array artista en el localstorage con una condicional e imprimir
    //alert(JSON.stringify(formData.artistas));
    const artista = formData.artistas.find(artista => artista.id === id);
    //alert(JSON.stringify(artista));
    //actualizar los datos del artista 
    artista.nombre = nombre;
    artista.genero = generoMusical;
    artista.descripcion = descripcion;
    //alert(JSON.stringify(formData));
    //actualizar los datos del localstorage
    localStorage.setItem('formData', JSON.stringify(formData));
    //redireccionar a la pagina de artistas

    alert('Actualización exitosa');
}