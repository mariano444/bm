import time
import uuid
from flask import Flask, render_template, redirect, url_for, flash, request
from forms import PublicationForm
from localidades import localidades_argentinas
import random, os
import requests  # Importar la librería requests para hacer peticiones HTTP

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MODIFIED_UPLOAD_FOLDER'] = 'modified_uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Máximo 16 MB

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODIFIED_UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

imagenes_publicadas = set()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PublicationForm()
    form.localidad.choices = [(loc, loc) for loc in localidades_argentinas]

    if form.validate_on_submit():
        # Capturar datos del formulario
        username = form.username.data
        password = form.password.data
        num_publications = form.num_publications.data
        selected_localities = form.localidad.data
        frases_lista = [frase.strip() for frase in form.phrases.data.split(",") if frase.strip()][:10]
        marca = form.marca.data
        modelo = form.modelo.data
        precio = form.precio.data
        millaje = form.millaje.data
        descripcion = form.descripcion.data

        # Manejar las imágenes subidas
        imagenes_subidas = request.files.getlist(form.imagenes.name)
        imagenes_guardadas = []
        for imagen in imagenes_subidas:
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagen.save(image_path)
                imagenes_guardadas.append(image_path)

        # Aquí se hace la llamada al bot local
        try:
            response = requests.post('http://localhost:5001/publicar', json={
                'username': username,
                'password': password,
                'num_publications': num_publications,
                'localities': selected_localities,
                'phrases': frases_lista,
                'brand': marca,
                'model': modelo,
                'price': precio,
                'mileage': millaje,
                'description': descripcion,
                'images': imagenes_guardadas
            })
            response.raise_for_status()  # Lanza un error si la respuesta no fue 2xx
            flash('Publicaciones realizadas con éxito!', 'success')
        except requests.exceptions.RequestException as e:
            flash(f'Error al publicar: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
