import time
import uuid
import requests
from flask import Flask, render_template, redirect, url_for, flash, request
from forms import PublicationForm
from localidades import localidades_argentinas
import random, os
from werkzeug.utils import secure_filename

# Configuración de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MODIFIED_UPLOAD_FOLDER'] = 'modified_uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Máximo 16 MB

# Crear carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODIFIED_UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta para el formulario
@app.route('/', methods=['GET', 'POST'])
def index():
    form = PublicationForm()
    form.localidad.choices = [(loc, loc) for loc in localidades_argentinas]

    if form.validate_on_submit():
        # Capturar los datos del formulario
        username = form.username.data
        password = form.password.data
        num_publications = form.num_publications.data
        selected_localities = form.localidad.data

        # Capturar frases del usuario
        frases_usuario = form.phrases.data
        frases_lista = [frase.strip() for frase in frases_usuario.split(",") if frase.strip()] 

        # Asegurar que no se excedan 10 frases
        if len(frases_lista) > 10:
            frases_lista = frases_lista[:10]

        # Extraer datos del formulario
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
            else:
                flash('Algunas imágenes no tienen un formato permitido. Solo se permiten archivos PNG, JPG, JPEG y GIF.', 'danger')
                return redirect(url_for('index'))

        # Preparar los datos para enviarlos al bot local
        data = {
            'username': username,
            'password': password,
            'num_publications': num_publications,
            'localities': selected_localities,
            'frases': frases_lista,
            'marca': marca,
            'modelo': modelo,
            'precio': precio,
            'millaje': millaje,
            'descripcion': descripcion
        }

        files = [('imagenes', (os.path.basename(image), open(image, 'rb'), 'image/jpeg')) for image in imagenes_guardadas]

        try:
            # Cambia localhost por la URL de tu túnel
            response = requests.post('https://459b117566c86eb05ad6c1e7e3d525ac.serveo.net/process', data=data, files=files)
            if response.status_code == 200:
                flash('Publicaciones realizadas con éxito!', 'success')
            else:
                flash(f'Error en el bot local: {response.text}', 'danger')
        except Exception as e:
            flash(f'Error al enviar los datos al bot local: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('index.html', form=form)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render asignará el puerto automáticamente
    app.run(host='0.0.0.0', port=port, debug=True)
