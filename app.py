import time
import uuid
import logging
from flask import Flask, render_template, redirect, url_for, flash, request
from forms import PublicationForm
from FacebookMarketplaceBot import FacebookMarketplaceBot
from localidades import localidades_argentinas
import random, os
from werkzeug.utils import secure_filename

# Configuración para Selenium en modo headless
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_headless_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    return webdriver.Chrome(options=chrome_options)

# Configurar la aplicación Flask
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

# Configurar el logger para monitorear las publicaciones
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable global para controlar las fotos ya publicadas
imagenes_publicadas = set()

# Función para formatear la descripción
def formatear_descripcion(texto):
    lineas = texto.split('\n')
    lineas_limpias = [f'"{linea.strip()} \\n"' for linea in lineas if linea.strip()]
    descripcion_formateada = 'description = (\n' + '    '.join(lineas_limpias) + '\n)'
    return descripcion_formateada

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PublicationForm()
    form.localidad.choices = [(loc, loc) for loc in localidades_argentinas]

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        num_publications = form.num_publications.data
        selected_localities = form.localidad.data

        frases_usuario = form.phrases.data
        frases_lista = [frase.strip() for frase in frases_usuario.split(",") if frase.strip()] 
        if len(frases_lista) > 10:
            frases_lista = frases_lista[:10]

        marca = form.marca.data
        modelo = form.modelo.data
        precio = form.precio.data
        millaje = form.millaje.data
        descripcion = form.descripcion.data
        descripcion_formateada = formatear_descripcion(descripcion)

        imagenes_subidas = request.files.getlist(form.imagenes.name)
        imagenes_guardadas = []
        for imagen in imagenes_subidas:
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                imagen.save(image_path)
                imagenes_guardadas.append(image_path)
            else:
                flash('Algunas imágenes no tienen un formato permitido.', 'danger')
                return redirect(url_for('index'))

        # Crear el bot con navegador en modo headless
        bot = FacebookMarketplaceBot(username, password, driver=get_headless_driver())
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

            imagenes_disponibles = list(set(imagenes_guardadas) - imagenes_publicadas)
            if len(imagenes_disponibles) == 0:
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

            imagenes_restantes = [img for img in imagenes_guardadas if img != primera_imagen]
            imagenes_para_publicar = [modified_image_path]

            max_fotos_a_cargar = min(18, len(imagenes_restantes))
            contador_imagenes = 1

            while contador_imagenes < max_fotos_a_cargar + 1 and imagenes_restantes:
                imagen_random = random.choice(imagenes_restantes)
                imagenes_para_publicar.append(imagen_random)
                imagenes_restantes.remove(imagen_random)
                contador_imagenes += 1

            try:
                bot.complete_form(form_data, descripcion_formateada, imagenes_para_publicar, [assigned_location])
                bot.click_button("Publicar")
                logger.info(f"Publicación {i + 1}/{num_publications} completada.")
                flash(f"Publicación {i + 1} completada.", 'success')
            except Exception as e:
                flash(f'Error al realizar la publicación {i + 1}: {str(e)}', 'danger')
                logger.error(f"Error al realizar la publicación {i + 1}: {str(e)}")
                continue

            time.sleep(random.uniform(30, 60))

        bot.close_browser()
        flash('Publicaciones realizadas con éxito!', 'success')
        return redirect(url_for('index'))

    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
