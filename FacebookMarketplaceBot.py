import os
import random
import time
import cv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from image_editor import apply_professional_design
from localidades import localidades_argentinas

class FacebookMarketplaceBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-gpu")  # Desactivar GPU
        chrome_options.add_argument("--window-size=1920x1080")  # Tamaño de ventana
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)

    def login(self):
        try:
            self.driver.get("https://www.facebook.com/")
            email_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "email")))
            email_field.send_keys(self.username)
            password_field = self.driver.find_element(By.NAME, "pass")
            password_field.send_keys(self.password)
            password_field.submit()
            self.wait.until(EC.url_contains("https://www.facebook.com/?sk=h_chr"))
            print("Inicio de sesión exitoso.")
        except TimeoutException:
            raise Exception("Tiempo de espera agotado durante el inicio de sesión.")
        except NoSuchElementException:
            raise Exception("No se encontraron los campos de correo electrónico o contraseña.")

    def complete_form(self, form_data, description, imagenes, selected_locations):
        try:
            self.driver.get("https://www.facebook.com/marketplace/create/vehicle")
            random_year = random.randint(2008, 2014)

            options = {
                "Tipo de vehículo": "Auto/camioneta",
                "Año": str(random_year),
                "Carrocería": "Familiar",
                "Estado del vehículo": "Excelente",
                "Transmisión": "Transmisión manual"
            }

            for category, option in options.items():
                self.select_option(category, option)

            for field_name, value in form_data.items():
                field = self.find_field_by_keyword(field_name)
                if field:
                    field.clear()
                    field.send_keys(value)

            self.fill_description(description)

            location_name = random.choice(selected_locations)
            if location_name:
                location_field = self.find_field_by_keyword("Ubicación")
                location_field.clear()
                location_field.send_keys(location_name)
                self.click_first_location_result()

            self.upload_photos(imagenes)
            self.click_button("Siguiente")
        except Exception as e:
            raise Exception(f"Error al completar el formulario: {e}")

    def upload_photos(self, imagenes):
        try:
            max_photos = 10
            imagenes = imagenes[:max_photos]

            for imagen_path in imagenes:
                absolute_path = os.path.abspath(imagen_path)
                input_field = self.driver.find_element(By.XPATH, "//input[@type='file']")
                input_field.send_keys(absolute_path)
                time.sleep(1)
                self.driver.execute_script('arguments[0].value=""', input_field)
        except Exception as e:
            raise Exception(f"Error al cargar las imágenes: {e}")

    def modify_and_save_photo(self, original_path, modified_path, frases):
        try:
            original_image = cv2.imread(original_path)
            if original_image is None:
                raise FileNotFoundError(f"No se pudo leer la imagen: {original_path}")

            modified_image = apply_professional_design(original_image, frases)
            cv2.imwrite(modified_path, modified_image)
            return modified_path
        except Exception as e:
            raise Exception(f"Error al modificar y guardar la imagen: {e}")

    def find_field_by_keyword(self, keyword):
        try:
            return self.driver.find_element(By.XPATH, f"//*[contains(text(), '{keyword}')]/following::input[1]")
        except NoSuchElementException:
            raise Exception(f"No se encontró el campo '{keyword}'")

    def fill_description(self, description):
        try:
            description_field = self.find_field_by_keyword("Descripción")
            if description_field:
                description_field.clear()
                description_field.send_keys(description)
        except Exception as e:
            raise Exception(f"Error al completar la descripción: {e}")

    def select_option(self, category, option_text):
        try:
            option_field = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{category}')]/following::div[contains(@aria-label, 'Menú desplegable')]")
            option_field.click()
            option = self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//span[text()='{option_text}']")))
            option.click()
        except Exception as e:
            raise Exception(f"Error al seleccionar la opción '{option_text}' para la categoría '{category}'")

    def click_button(self, button_text):
        try:
            button = self.driver.find_element(By.XPATH, f"//span[text()='{button_text}']/ancestor::button")
            button.click()
        except NoSuchElementException:
            raise Exception(f"No se encontró el botón '{button_text}'")

    def assign_locations(self, num_publications, selected_locations):
        return random.choices(selected_locations, k=num_publications)

    def click_first_location_result(self):
        try:
            location_result = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//ul/li[1]")))
            location_result.click()
        except TimeoutException:
            raise Exception("No se pudo seleccionar la ubicación.")

    def close_browser(self):
        self.driver.quit()
