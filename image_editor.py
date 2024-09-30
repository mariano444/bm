import cv2
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import matplotlib.pyplot as plt
import os

# Colores de fondo aleatorios para las frases
background_colors = [
    (0, 102, 204),   # Azul
    (255, 87, 51),   # Coral
    (60, 179, 113),  # Verde Medio
    (220, 20, 60),   # Rojo Carmesí
    (138, 43, 226)   # Azul Violeta
]

# Paleta de colores para el texto
text_colors = [
    (255, 255, 255),  # Blanco
    (0, 0, 0),        # Negro
    (255, 215, 0),    # Oro
    (255, 20, 147),   # Rosa Profundo
    (135, 206, 235)   # Azul Claro
]

# Funciones de apoyo
def get_font(size):
    font_path = "fonts/Roboto-Bold.ttf"
    try:
        return ImageFont.truetype(font_path, size=size)
    except IOError:
        return ImageFont.load_default()

def add_text(draw, position, text, font, text_color):
    shadow_color = (0, 0, 0)
    x, y = position
    draw.text((x + 2, y + 2), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=text_color)

def add_random_text(image, text):
    """
    Añade texto aleatorio con un fondo estilizado a la imagen en una posición aleatoria.
    """
    width, height = image.size

    draw = ImageDraw.Draw(image)

    # Cargar una fuente aleatoria
    font_size = random.randint(int(width / 15), int(width / 15))
    font = get_font(font_size)

    # Calcular el tamaño del texto
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    # Obtener una posición aleatoria para el texto
    x, y = get_random_position(image, (text_width, text_height))

    # Añadir fondo estilizado (gradiente y sombra)
    margin = 15
    rect_x0 = x - margin
    rect_y0 = y - margin
    rect_x1 = x + text_width + margin
    rect_y1 = y + text_height + margin
    background_color = random.choice(background_colors)

    # Crear un gradiente para el fondo
    gradient = Image.new('RGBA', (rect_x1 - rect_x0, rect_y1 - rect_y0), background_color)
    for i in range(gradient.width):
        gradient_color = (
            int(background_color[0] * (1 - i / gradient.width)),
            int(background_color[1] * (1 - i / gradient.width)),
            int(background_color[2] * (1 - i / gradient.width)),
            255
        )
        ImageDraw.Draw(gradient).line([(i, 0), (i, gradient.height)], fill=gradient_color)

    # Añadir sombra al fondo
    shadow = gradient.filter(ImageFilter.GaussianBlur(radius=5))
    image.paste(shadow, (rect_x0 + 4, rect_y0 + 4), shadow)
    image.paste(gradient, (rect_x0, rect_y0), gradient)

    # Añadir el texto encima del fondo
    text_color = random.choice(text_colors)
    add_text(draw, (x, y), text, font, text_color)

def get_random_position(image, text_size):
    """
    Obtiene una posición aleatoria para colocar el texto en la imagen.
    """
    width, height = image.size
    max_x = width - text_size[0] - 20  # Asegurar que el texto no se salga de los bordes
    max_y = height - text_size[1] - 20  # Asegurar que el texto no se salga de los bordes
    x = random.randint(20, max_x)
    y = random.randint(20, max_y)
    return x, y

def add_corner_text(image, text):
    """
    Añade el texto "¡Contáctanos ahora!" en una de las cuatro esquinas de la imagen.
    """
    width, height = image.size

    draw = ImageDraw.Draw(image)

    # Cargar una fuente
    font_size = int(width / 30)
    font = get_font(font_size)

    # Calcular el tamaño del texto
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]

    # Definir las posiciones de las cuatro esquinas
    corners = [
        (20, 20),  # Esquina superior izquierda
        (width - text_width - 20, 20),  # Esquina superior derecha
        (20, height - text_height - 20),  # Esquina inferior izquierda
        (width - text_width - 20, height - text_height - 20)  # Esquina inferior derecha
    ]

    # Seleccionar aleatoriamente una de las esquinas
    corner = random.choice(corners)
    text_x, text_y = corner

    # Añadir fondo estilizado (gradiente y sombra)
    margin = 10
    rect_x0 = text_x - margin
    rect_y0 = text_y - margin
    rect_x1 = text_x + text_width + margin
    rect_y1 = text_y + text_height + margin
    background_color = random.choice(background_colors)

    # Crear un gradiente para el fondo
    gradient = Image.new('RGBA', (rect_x1 - rect_x0, rect_y1 - rect_y0), background_color)
    for i in range(gradient.width):
        gradient_color = (
            int(background_color[0] * (1 - i / gradient.width)),
            int(background_color[1] * (1 - i / gradient.width)),
            int(background_color[2] * (1 - i / gradient.width)),
            255
        )
        ImageDraw.Draw(gradient).line([(i, 0), (i, gradient.height)], fill=gradient_color)

    # Añadir sombra al fondo
    shadow = gradient.filter(ImageFilter.GaussianBlur(radius=5))
    image.paste(shadow, (rect_x0 + 3, rect_y0 + 3), shadow)
    image.paste(gradient, (rect_x0, rect_y0), gradient)

    # Añadir el texto encima del fondo
    text_color = (255, 255, 255)  # Blanco
    add_text(draw, (text_x, text_y), text, font, text_color)

def apply_professional_design(image, frases):
    """
    Aplica un diseño profesional a la imagen utilizando frases proporcionadas y elementos gráficos.
    """
    try:
        # Convertir a imagen PIL para manipulaciones avanzadas
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Añadir elementos decorativos, usando las frases proporcionadas
        pil_image = add_decorative_elements(pil_image, frases)

        # Convertir de nuevo a OpenCV
        image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

        return image
    except Exception as e:
        print(f"Error al aplicar el diseño profesional: {e}")
        return image

def add_decorative_elements(image, frases):
    """
    Añade elementos decorativos a la imagen usando las frases proporcionadas.
    """
    try:
        for _ in range(1):  # Añadir un texto aleatorio
            text = random.choice(frases) if frases else "Texto predeterminado"
            add_random_text(image, text)

        # Añadir el texto específico "¡Contáctanos ahora!" en una esquina
        add_corner_text(image, "¡Contáctanos ahora!")

        return image
    except Exception as e:
        print(f"Error al añadir elementos decorativos: {e}")
        return image


