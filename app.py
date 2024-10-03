import time
import uuid
from flask import Flask, render_template, redirect, url_for, flash, request
from forms import PublicationForm
from FacebookMarketplaceBot import FacebookMarketplaceBot
from localidades import localidades_argentinas
import random, os
from werkzeug.utils import secure_filename

# Configuración de Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MODIFIED_UPLOAD_FOLDER'] = 'modified_uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Máximo 16 MB

# Crear carpetas si no existen
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['MODIFIED_UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Función para verificar si el archivo es permitido
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Variable global para las imágenes publicadas
imagenes_publicadas = set()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PublicationForm()
    form.localidad.choices = [(loc, loc) for loc in localidades_argentinas]

    if form.validate_on_submit():
        # Datos del formulario
        username = form.username.data
        password = form.password.data
        num_publications = form.num_publications.data
        selected_localities = form.localidad.data
        marca = form.marca.data
        modelo = form.modelo.data
        precio = form.precio.data
        millaje = form.millaje.data
        descripcion = form.descripcion.data

        # Frases ingresadas por el usuario
        frases_usuario = form.phrases.data
        frases_lista = [frase.strip() for frase in frases_usuario.split(",") if frase.strip()] 
        frases_lista = frases_lista[:10]  # Limitar a 10 frases

        # Manejo de las imágenes subidas
        imagenes_subidas = request.files.getlist(form.imagenes.name)
        imagenes_guardadas = []
        for imagen in imagenes_subidas:
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagen.save(image_path)
                imagenes_guardadas.append(image_path)
            else:
                flash('Formato de archivo no permitido. Solo se permiten PNG, JPG, JPEG y GIF.', 'danger')
                return redirect(url_for('index'))

        # Creación y login del bot
        bot = FacebookMarketplaceBot(username, password)
        try:
            bot.login()
        except Exception as e:
            flash(f'Error al iniciar sesión: {str(e)}', 'danger')
            return redirect(url_for('index'))

        localidades_asignadas = bot.assign_locations(num_publications, selected_localities)

        for i in range(num_publications):
            form_data = {
                "Marca": marca,
                "Modelo": modelo,
                "Precio": precio,
                "Millaje": millaje
            }

            assigned_location = localidades_asignadas[i]

            # Seleccionar imágenes no publicadas aún
            imagenes_disponibles = list(set(imagenes_guardadas) - imagenes_publicadas)

            if not imagenes_disponibles:
                imagenes_publicadas.clear()
                imagenes_disponibles = imagenes_guardadas

            primera_imagen = random.choice(imagenes_disponibles)
            imagenes_publicadas.add(primera_imagen)

            unique_id = str(uuid.uuid4())
            filename, file_extension = os.path.splitext(os.path.basename(primera_imagen))
            modified_image_path = os.path.join(app.config['MODIFIED_UPLOAD_FOLDER'], f"{filename}_modified_{unique_id}{file_extension}")

            if not os.path.exists(modified_image_path):
                try:
                    modified_image_path = bot.modify_and_save_photo(primera_imagen, modified_image_path, frases_lista)
                except Exception as e:
                    flash(f'Error al modificar la imagen: {str(e)}', 'danger')
                    continue

            imagenes_para_publicar = [modified_image_path]
            imagenes_restantes = [img for img in imagenes_guardadas if img != primera_imagen]
            max_fotos_a_cargar = min(18, len(imagenes_restantes))

            for imagen in random.sample(imagenes_restantes, max_fotos_a_cargar):
                imagenes_para_publicar.append(imagen)

            try:
                bot.complete_form(form_data, descripcion, imagenes_para_publicar, [assigned_location])
                bot.click_button("Publicar")
                print(f"Publicación {i + 1}/{num_publications} completada.")
            except Exception as e:
                flash(f'Error en la publicación {i + 1}: {str(e)}', 'danger')
                continue

            time.sleep(random.uniform(30, 60))

        bot.close_browser()
        flash('Publicaciones realizadas con éxito!', 'success')
        return redirect(url_for('index'))

    return render_template('index.html', form=form)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
