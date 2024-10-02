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
from selenium.webdriver.common.action_chains import ActionChains
from image_editor import apply_professional_design
from localidades import localidades_argentinas  # Importamos las localidades desde el archivo

class FacebookMarketplaceBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--disable-notifications")
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
            self.wait.until(EC.url_matches("https://www.facebook.com/?sk=h_chr"))
            print("Inicio de sesión exitoso.")
        except TimeoutException:
            print("Tiempo de espera agotado durante el inicio de sesión.")
        except NoSuchElementException:
            print("No se encontró el campo de correo electrónico o contraseña.")
        except Exception as e:
            print(f"Error durante el inicio de sesión: {e}")

    def complete_form(self, form_data, description, imagenes, selected_locations):
        try:
            self.driver.get("https://www.facebook.com/marketplace/create/vehicle")
            print("Redireccionado a Marketplace.")

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
                    print(f"Campo '{field_name}' completado automáticamente con '{value}'.")
                else:
                    print(f"No se encontró el campo '{field_name}'.")

            self.fill_description(description)

            # Limpiar y asignar la ubicación
            location_name = random.choice(selected_locations)
            if location_name:
                print(f"Ubicación seleccionada: {location_name}")
                location_field = self.find_field_by_keyword("Ubicación")
                if location_field:
                    location_field.clear() 
                    location_field.send_keys(Keys.CONTROL + "a")
                    location_field.send_keys(Keys.DELETE) # Limpiar el campo antes de ingresar la nueva ubicación
                    location_field.send_keys(location_name)
                    self.click_first_location_result()

            # Subir las imágenes
            self.upload_photos(imagenes)
            self.click_button("Siguiente")

        except Exception as e:
            print(f"Error al completar el formulario: {e}")

    def upload_photos(self, imagenes):
        try:
            max_photos = 10  # Limitar a 10 fotos como máximo
            imagenes = imagenes[:max_photos]  # Limitar a las primeras 10 imágenes

            for index, imagen_path in enumerate(imagenes):
                absolute_path = os.path.abspath(imagen_path)  # Asegúrate de que el path sea absoluto
                
                input_field = self.driver.find_element(By.XPATH, "//input[@type='file']")
                input_field.send_keys(absolute_path)  # Usa el path absoluto aquí
                print(f"Imagen {imagen_path} cargada.")
                time.sleep(1)  # Pausa entre cargas de imágenes
                
                # Limpiar el campo de entrada para evitar duplicados
                self.driver.execute_script('arguments[0].value=""', input_field)

            print(f"Total de imágenes cargadas: {len(imagenes)}")
        except Exception as e:
            print(f"Error al cargar las imágenes: {e}")


    def modify_and_save_photo(self, original_path, modified_path, frases):
        """
        Modifica la imagen usando la función apply_professional_design y la guarda.
        """
        try:
            # Leer la imagen original usando OpenCV
            original_image = cv2.imread(original_path)
            if original_image is None:
                raise FileNotFoundError(f"No se pudo leer la imagen: {original_path}")

            # Aplicar el diseño profesional usando el script de edición
            modified_image = apply_professional_design(original_image, frases)
            
            # Guardar la imagen modificada
            cv2.imwrite(modified_path, modified_image)
            print(f"Imagen modificada guardada en {modified_path}")
            return modified_path
        except Exception as e:
            print(f"Error al modificar y guardar la imagen: {e}")
            return None

    def find_field_by_keyword(self, keyword):
        try:
            field = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{keyword}')]/following::input[1]")
            return field
        except NoSuchElementException:
            return None

    def fill_description(self, description):
        try:
            description_field = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea.x1i10hfl")))
            description_field.clear()
            description_field.send_keys(description)
            print("Descripción completada automáticamente.")
        except TimeoutException:
            print("Tiempo de espera agotado para el campo de descripción.")
        except Exception as e:
            print(f"Error al completar la descripción: {e}")

    def select_option(self, category, option):
        try:
            label_element = self.wait.until(EC.visibility_of_element_located((By.XPATH, f"//label[contains(@aria-label, '{category}')]")))
            self.driver.execute_script("arguments[0].scrollIntoView();", label_element)
            self.driver.execute_script("arguments[0].click();", label_element)

            option_element = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{option}']")))
            self.driver.execute_script("arguments[0].scrollIntoView();", option_element)
            time.sleep(1)

            action = ActionChains(self.driver)
            action.move_to_element(option_element).click().perform()
            print(f"Opción '{option}' seleccionada en '{category}'.")

        except TimeoutException:
            print(f"No se pudo encontrar la opción '{option}' en '{category}'.")
        except Exception as e:
            print(f"Error al seleccionar la opción '{option}' en '{category}': {e}")

    def click_button(self, button_text):
        try:
            button = self.wait.until(EC.element_to_be_clickable((By.XPATH, f"//span[text()='{button_text}']")))
            self.driver.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(2)
            button.click()
            print(f"Botón '{button_text}' clicado.")
        except TimeoutException:
            print(f"No se pudo encontrar el botón '{button_text}'.")
        except Exception as e:
            print(f"Error al hacer clic en el botón '{button_text}': {e}")

    def close_browser(self):
        self.driver.quit()
        print("Navegador cerrado.")

    def upload_photos_from_folder(self, folder_name, modified_folder_name, max_photos=10):
        try:
            folder_path = os.path.join(os.getcwd(), folder_name)
            modified_folder_path = os.path.join(os.getcwd(), modified_folder_name)
            if not os.path.exists(modified_folder_path):
                os.makedirs(modified_folder_path)
            photos = os.listdir(folder_path)
            random.shuffle(photos)
            num_photos_to_upload = min(max_photos, len(photos))
            photo_count = 0
            for index, photo in enumerate(photos):
                if photo_count >= num_photos_to_upload:
                    break
                photo_path = os.path.join(folder_path, photo)
                modified_photo_path = os.path.join(modified_folder_path, f"modified_{photo}")
                if index == 0:
                    self.modify_and_save_photo(photo_path, modified_photo_path)
                else:
                    modified_photo_path = photo_path
                input_field = self.driver.find_element(By.XPATH, "//input[@type='file']")
                input_field.send_keys(modified_photo_path)
                print(f"Fotografía {photo} cargada.")
                photo_count += 1
                time.sleep(1)
                photos.remove(photo)
                self.driver.execute_script('arguments[0].value=""', input_field)
        except Exception as e:
            print(f"Error al cargar las fotos: {e}")

    def find_field_by_keyword(self, keyword):
        try:
            # Encontrar el campo basado en la palabra clave (ej. 'Ubicación')
            field = self.driver.find_element(By.XPATH, f"//*[contains(text(), '{keyword}')]/following::input[1]")
            field.clear()  # Limpiar el campo antes de escribir
            return field
        except NoSuchElementException:
            return None

    def click_first_location_result(self):
        try:
            # Asegurarse de que el elemento es visible y scroll hacia él
            location_results = self.wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//ul[contains(@role,'listbox')]//li")))
            
            # Desplazar hasta el primer resultado de la lista de ubicaciones
            if location_results:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", location_results[0])

                # Esperar explícitamente a que el elemento esté clicable
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(location_results[0])).click()
                print("Se hizo clic en el primer resultado de ubicación.")
            else:
                print("No se encontraron resultados de ubicación.")
        except TimeoutException:
            print("Tiempo de espera agotado para los resultados de ubicación.")
        except Exception as e:
            print(f"Error al hacer clic en el primer resultado de ubicación: {e}")

    def check_all_fields_complete(self, form_data):
        try:
            incomplete_fields = []
            for field_name in form_data.keys():
                field = self.find_field_by_keyword(field_name)
                if field and not field.get_attribute('value'):
                    incomplete_fields.append(field_name)

            if incomplete_fields:
                print(f"Campos incompletos: {', '.join(incomplete_fields)}")
                return False
            return True
        except Exception as e:
            print(f"Error al verificar campos completos: {e}")
            return False

    def assign_locations(self, num_publications, selected_locations):
        """
        Asigna localidades de forma tal que no se repitan hasta que se hayan usado todas.
        Cuando se acaben, se reutilizan en un nuevo ciclo.
        """
        result = []
        if len(selected_locations) >= num_publications:
            result = random.sample(selected_locations, num_publications)
        else:
            # Si hay menos localidades que publicaciones, distribuir de manera balanceada
            cycle_locations = selected_locations * (num_publications // len(selected_locations)) + selected_locations[:num_publications % len(selected_locations)]
            random.shuffle(cycle_locations)  # Reorganizar las localidades para evitar un patrón predecible
            result = cycle_locations

        return result

   
    def get_random_location_name(self):
        try:
            if localidades_argentinas:
                available_locations = set(localidades_argentinas) - self.used_locations
                if available_locations:
                    location_name = random.choice(list(available_locations))
                    self.used_locations.add(location_name)
                    return location_name
                else:
                    raise Exception("Todas las localidades han sido utilizadas.")
            else:
                raise Exception("No se encontraron localidades dentro de Argentina.")
        except Exception as e:
            print(f"Error al obtener el nombre de la ubicación aleatoria: {e}")
            return None
