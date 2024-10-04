from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectMultipleField, IntegerField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, NumberRange
from flask_wtf.file import FileAllowed

class PublicationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    num_publications = IntegerField('Número de publicaciones', validators=[DataRequired(), NumberRange(min=1)])
    localidad = SelectMultipleField('Localidad', validators=[DataRequired()], coerce=str)
    
    # Nuevos campos personalizados
    marca = StringField('Marca', validators=[DataRequired()])
    modelo = StringField('Modelo', validators=[DataRequired()])
    precio = StringField('Precio', validators=[DataRequired()])
    millaje = StringField('Millaje', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])

    # Cambiar 'frases' a 'phrases' para hacer coincidir con el HTML
    phrases = TextAreaField('Frases (las frases separadas con , (coma))', validators=[DataRequired()])
    
    # Campo para subir imágenes (máximo 30)
    imagenes = FileField('Subir imágenes', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Solo imágenes JPG y PNG!')])

    submit = SubmitField('Realizar Publicaciones')
