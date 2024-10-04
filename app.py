from flask import Flask, render_template, redirect, url_for, flash, request
from flask_socketio import SocketIO
from forms import PublicationForm
import os, requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Crear carpetas si no existen
os.makedirs('uploads', exist_ok=True)
os.makedirs('modified_uploads', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PublicationForm()
    form.localidad.choices = [(loc, loc) for loc in localidades_argentinas]

    if form.validate_on_submit():
        # Capturar datos y procesar el formulario
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

        imagenes_subidas = request.files.getlist(form.imagenes.name)
        imagenes_guardadas = []
        for imagen in imagenes_subidas:
            if imagen and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                image_path = os.path.join('uploads', filename)
                imagen.save(image_path)
                imagenes_guardadas.append(image_path)

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
            response = requests.post('https://3464-181-99-182-19.ngrok-free.app/process', data=data, files=files)
            if response.status_code == 200:
                flash('Publicaciones realizadas con éxito!', 'success')
            else:
                flash(f'Error en el bot local: {response.text}', 'danger')
        except Exception as e:
            flash(f'Error al enviar los datos al bot local: {str(e)}', 'danger')

        return redirect(url_for('index'))

    return render_template('index.html', form=form)

# Manejar mensajes de progreso de app1.py
@socketio.on('progress')
def handle_progress(data):
    emit('progress', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
