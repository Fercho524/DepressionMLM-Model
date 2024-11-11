import os
import json
import random
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# Constantes de selectores para popups
LOGIN_POPUP_CLOSE_XPATH = '//div[@class="x92rtbv x10l6tqk x1tk7jg1 x1vjfegm"]'
SCROLL_BLOCK_POPUP_CLASS = "__fb-light-mode x1n2onr6 xzkaem6"
POST_TEXT_XPATH = '//div[contains(@class,"html-div")]//div[@class="xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a"]'
POST_IMG_XPATH = '//div[contains(@class,"html-div")]//img[@referrerpolicy="origin-when-cross-origin"]'

class FacebookScraper:
    def __init__(self, base_dir=None, headless=True):
        options = Options()
        options.headless = headless
        self.driver = webdriver.Firefox(options=options)
        self.base_dir = base_dir if base_dir else os.getcwd()


    def download_user_posts(self, profile_link, private_profile=False, credentials={}):
        """Descarga publicaciones de un perfil de Facebook y las guarda en el directorio especificado."""
        try:
            self.driver.get(profile_link)
            username = profile_link.split("/")[-1]

            # Configurar el directorio de almacenamiento
            user_dir = os.path.join(self.base_dir, f"{username}_data")
            os.makedirs(user_dir, exist_ok=True)

            # Manejo de popups y login
            if not private_profile:
                self._close_login_popup()
                self._hide_scroll_block_popup()
            else:
                self._login(credentials)

            # Desplazarse para cargar publicaciones
            self._scroll_page()

            # Obtener textos e imágenes
            textos = self.driver.find_elements("xpath", POST_TEXT_XPATH)
            imagenes = self.driver.find_elements("xpath", POST_IMG_XPATH)

            # Crear objeto de usuario
            user_object = self._create_user_object(username, textos, imagenes, user_dir)

            # Guardar datos en JSON
            self._save_user_data(user_object, user_dir)

            print(f"Descarga completa para el usuario {username}. Archivos guardados en {os.path.abspath(user_dir)}")
            return user_object, os.path.abspath(user_dir)

        except WebDriverException as e:
            print(f"Error de WebDriver: {e}")
        finally:
            self.driver.quit()


    def _close_login_popup(self):
        """Intenta cerrar el popup principal de inicio de sesión."""
        try:
            login_btn = self.driver.find_element("xpath", LOGIN_POPUP_CLOSE_XPATH)
            login_btn.click()
            print("Popup de inicio de sesión cerrado.")
        except NoSuchElementException:
            print("No se encontró el popup de inicio de sesión principal.")


    def _hide_scroll_block_popup(self):
        """Oculta el popup que bloquea el scroll en la página."""
        try:
            popup_block = self.driver.find_element("class name", SCROLL_BLOCK_POPUP_CLASS)
            self.driver.execute_script("arguments[0].style.display = 'none';", popup_block)
            print("Popup bloqueador de scroll cerrado.")
        except NoSuchElementException:
            print("No se encontró el popup bloqueador de scroll.")


    def _login(self, credentials):
        """Inicia sesión si el perfil es privado."""
        try:
            self.driver.find_element("name", "email").send_keys(credentials["username"])
            self.driver.find_element("name", "pass").send_keys(credentials["password"])
            self.driver.find_element("name", "login").click()
            sleep(5)
            print("Sesión iniciada en Facebook.")
        except NoSuchElementException:
            print("No se encontraron los campos de inicio de sesión.")


    def _scroll_page(self, scroll_count=10):
        """Realiza un scroll para cargar las publicaciones de la página."""
        sleep(random.uniform(10, 15))

        for _ in range(scroll_count):
            self._hide_scroll_block_popup()
            self.driver.execute_script("window.scrollBy(0, 5000);")
            sleep(random.uniform(5, 10))


    def _create_user_object(self, username, textos, imagenes, user_dir):
        """Crea el objeto de usuario con textos e imágenes descargadas."""
        user_object = {
            "username": username,
            "depressed": 0,
            "response": "None",
            "posts": [],
            "prompt": ""
        }
        
        for i in range(len(textos) - 1, 0, -1):
            texto = textos[i].text
            img_path = os.path.join(user_dir, f"{username}_{i}.png")

            # Intentar guardar imagen
            try:
                with open(img_path, "wb") as img_file:
                    img_file.write(imagenes[i].screenshot_as_png)
                if os.path.getsize(img_path) < 1024:
                    os.remove(img_path)
                    img_path = "None"
            except Exception as e:
                print(f"Error al guardar imagen para el post {i}: {e}")
                img_path = "None"

            post = {
                "id": len(textos) - i,
                "text": texto,
                "image_path": f"{username}_{i}.png",
                "image_description": "None"
            }
            user_object["posts"].append(post)

        return user_object


    def _save_user_data(self, user_object, user_dir):
        """Guarda los datos del usuario en un archivo JSON."""
        json_path = os.path.join(user_dir, f"user.json")
        try:
            with open(json_path, "w", encoding="utf-8") as file:
                json.dump(user_object, file, ensure_ascii=False, indent=4)
            print(f"Datos guardados en {json_path}")
        except IOError as e:
            print(f"Error al guardar el archivo JSON: {e}")


if __name__ == "__main__":
    # Crear instancia del scraper
    scraper = FacebookScraper(base_dir="Working", headless=True)

    # Descargar publicaciones
    user_data, user_data_dir = scraper.download_user_posts(
        profile_link="https://facebook.com/username",
        private_profile=False,
        credentials={
            "username": "your_username",
            "password": "your_password"
        }
    )
    print(f"Los datos se han guardado en: {user_data_dir}")
