import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QFrame, QGroupBox, QCheckBox, QScrollBar, QTextEdit, QProgressBar
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLineEdit, QCheckBox, QRadioButton, QGroupBox,
                             QDateTimeEdit, QTextEdit, QGridLayout, QScrollArea, QProgressBar, QButtonGroup, QSizePolicy, QSpacerItem,QDialog)

import shutil
import re

#evaluar extesion o ruta completa y copiar el archivo.

class SearchFilesThread(QThread):
    update_progress = pyqtSignal(int)
    finished_searching = pyqtSignal(int, int)

    def __init__(self, files, path_to_files, path_to_log, path_to_found, search_patterns, logical_operator="AND", use_regex=False, file_extension=None, max_file_size_mb=None):
        super().__init__()
        self.files = files
        self.path_to_files = path_to_files
        self.path_to_log = path_to_log
        self.path_to_found = path_to_found
        self.search_patterns = search_patterns
        self.logical_operator = logical_operator
        self.use_regex = use_regex
        self.file_extension = file_extension
        self.max_file_size_mb = max_file_size_mb
        self.total_files = len(files)

    def run(self):
        success = 0
        fail = 0

        if not os.path.isdir(self.path_to_files):
            raise ValueError(f"La carpeta {self.path_to_files} no existe.")

        # Convertir términos a regex si no se usa regex
        if not self.use_regex:
            self.search_patterns = [re.escape(pattern) for pattern in self.search_patterns]

        # Compilar expresiones regulares
        regex_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.search_patterns]

        for idx, file_path in enumerate(self.files):
            if self.file_extension and not file_path.endswith(self.file_extension):
                continue

            if self.max_file_size_mb and os.path.getsize(file_path) > self.max_file_size_mb * 1024 * 1024:
                print(f"Saltando archivo grande: {file_path}")
                continue

            if os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
                    matching_lines = []
                    for line in file:
                        line = line.strip()
                        matches = [bool(pattern.search(line)) for pattern in regex_patterns]

                        # Evaluar la operación lógica avanzada
                        if self.logical_operator == "AND":
                            match_found = all(matches)
                        elif self.logical_operator == "OR":
                            match_found = any(matches)
                        elif self.logical_operator == "NOT":
                            match_found = not any(matches)
                        elif self.logical_operator == "XOR":  # Exclusivo (solo una coincidencia)
                            match_found = sum(matches) == 1
                        elif self.logical_operator == "NAND":  # Al menos una palabra debe faltar
                            match_found = not all(matches)
                        elif self.logical_operator == "NOR":  # Ninguna debe aparecer
                            match_found = not any(matches)
                        else:
                            raise ValueError("Operador lógico inválido. Usa 'AND', 'OR', 'NOT', 'XOR', 'NAND', 'NOR'.")

                        if match_found:
                            matching_lines.append(line)

                if matching_lines:
                    try:
                        shutil.move(file_path, self.path_to_found)
                        success += 1
                    except Exception as e:
                        with open(self.path_to_log, "a") as log_file:
                            log_file.write(f"\nError moviendo {file_path}: {str(e)}")
                        fail += 1

            self.update_progress.emit(int((idx + 1) / self.total_files * 100))

        self.finished_searching.emit(success, fail)


class CopyFilesThread(QThread):
    update_progress = pyqtSignal(int)
    finished_copying = pyqtSignal(int, int)

    def __init__(self, files, path_to_files, path_to_log):
        super().__init__()
        self.files = files
        self.path_to_files = path_to_files
        self.path_to_log = path_to_log
        self.total_files = len(files)



    def run(self):
        success = 0
        fail = 0
        for idx, line in enumerate(self.files):
            line = line.strip()
            try:
                shutil.copy(line, self.path_to_files)
                success += 1
            except Exception as e:
                with open(self.path_to_log, "a") as log_file:
                    log_file.write("\n" + line)
                fail += 1

            self.update_progress.emit(int((idx + 1) / self.total_files * 100))

        self.finished_copying.emit(success, fail)



class CopyFiles(QWidget):
    path = os.getcwd()
    path_to_files = os.path.join(path,'anon','files')
    path_to_found = os.path.join(path_to_files, 'found')
    path_to_log = os.path.join(path_to_files, 'log', 'copyfiles.log')
    total_success = 0  # Add this line

    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Copy Files")
        self.setMinimumSize(QSize(990, 930))

        self.cf_base_gridlayout = QGridLayout(self)
        self.frame = QFrame(self)
        self.frame.setMinimumSize(QSize(850, 850))
        self.cf_inner_grid_layout = QGridLayout(self.frame)

        # Frame para los botones principales
        self.cf_button_frame = QFrame(self.frame)
        self.cf_button_grid_layout = QGridLayout(self.cf_button_frame)

        # Frame para los botones dinámicos
        self.cf_variable_button_frame = QFrame(self.frame)
        self.cf_variable_button_frame.setFrameShape(QFrame.StyledPanel)
        self.cf_variable_button_frame.setFrameShadow(QFrame.Raised)

        # 🔹 IMPORTANTE: Agregar cf_variable_button_frame a la interfaz
        self.cf_inner_grid_layout.addWidget(self.cf_variable_button_frame, 5, 0, 1, 4)

        # Agregar el frame principal de botones a la interfaz
        self.cf_inner_grid_layout.addWidget(self.cf_button_frame, 4, 0, 1, 4)

        # Configurar el frame en la ventana principal
        self.cf_base_gridlayout.addWidget(self.frame, 0, 0, 1, 1)

        # Crear un QGroupBox para contener los botones
        self.mode_selector_groupbox = QGroupBox("Selector de Modos", self.frame)
        self.mode_selector_groupbox.setObjectName(u"mode_selector_groupbox")
        self.mode_selector_groupbox.setMinimumSize(QSize(300, 100))  # Ajusta el tamaño según sea necesario

        # Crear un QVBoxLayout para el QGroupBox
        self.mode_selector_layout = QHBoxLayout(self.mode_selector_groupbox)

        # Crear los botones
        self.cf_copy_files_button = QPushButton(self.mode_selector_groupbox)
        self.cf_copy_files_button.setObjectName(u"cf_copy_files_button")
        self.cf_copy_files_button.setMinimumSize(QSize(120, 35))
        self.cf_copy_files_button.setMaximumSize(QSize(600, 35))

        self.cf_search_local_button = QPushButton(self.mode_selector_groupbox)
        self.cf_search_local_button.setObjectName(u"cf_search_local_button")
        self.cf_search_local_button.setMinimumSize(QSize(120, 35))
        self.cf_search_local_button.setMaximumSize(QSize(600, 35))

        # Añadir los botones al QVBoxLayout del QGroupBox
        self.mode_selector_layout.addWidget(self.cf_copy_files_button)
        self.mode_selector_layout.addWidget(self.cf_search_local_button)

        # Añadir el QGroupBox al cf_inner_grid_layout
        self.cf_inner_grid_layout.addWidget(self.mode_selector_groupbox, 4, 0, 1, 4)

        # Aplicar el QSS personalizado
        qss = """
        QPushButton#cf_copy_files_button, QPushButton#cf_search_local_button {
            background-color: #555; /* Color de fondo gris oscuro */
            color: #fff; /* Color de texto blanco */
            border: 2px solid #777; /* Borde gris más claro */
            border-radius: 5px; /* Bordes redondeados */
            padding: 5px; /* Espaciado interno */
        }

        QPushButton#cf_copy_files_button:hover, QPushButton#cf_search_local_button:hover {
            background-color: #777; /* Color de fondo más claro al pasar el ratón */
        }

        QPushButton#cf_copy_files_button:pressed, QPushButton#cf_search_local_button:pressed {
            background-color: #333; /* Color de fondo más oscuro al presionar */
        }
        """
        self.cf_copy_files_button.setStyleSheet(qss)
        self.cf_search_local_button.setStyleSheet(qss)

        # Inicializar elementos
        self.init_labels()
        self.init_text_inputs()
        self.init_progress_bar()
        self.copy_init_buttons()


        self.test_paths()


        self.cf_copy_files_button.clicked.connect(self.copy_init_buttons)
        self.cf_search_local_button.clicked.connect(self.search_in_local_buttons)

        self.cf_integer_input.setText("4")


        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)


    def copy_init_buttons(self):
        """Inicializa los botones dentro de cf_variable_button_frame, permitiendo recrearlos dinámicamente."""

        # 🔹 Verificar si cf_variable_button_frame ya tiene un layout
        if self.cf_variable_button_frame.layout() is None:
            self.cf_button_grid_layout = QGridLayout()  # Crear el layout
            self.cf_variable_button_frame.setLayout(self.cf_button_grid_layout)  # Asignarlo al frame
        else:
            self.cf_button_grid_layout = self.cf_variable_button_frame.layout()

            # 🔹 Si el layout ya existía, eliminar los widgets antiguos
            while self.cf_button_grid_layout.count():
                item = self.cf_button_grid_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # 🔹 Crear y agregar botones al layout dinámico
        self.cf_button_copy = QPushButton("Copiar", self.cf_variable_button_frame)
        self.cf_button_copy.setMinimumSize(QSize(120, 35))
        self.cf_button_grid_layout.addWidget(self.cf_button_copy, 0, 0)

        self.cf_button_delete = QPushButton("Vaciar Destino", self.cf_variable_button_frame)
        self.cf_button_delete.setMinimumSize(QSize(120, 35))
        self.cf_button_grid_layout.addWidget(self.cf_button_delete, 0, 1)

        self.cf_button_log = QPushButton("Ver Log", self.cf_variable_button_frame)
        self.cf_button_log.setMinimumSize(QSize(120, 35))
        self.cf_button_grid_layout.addWidget(self.cf_button_log, 0, 2)

        self.cf_button_output = QPushButton("Abrir Destino", self.cf_variable_button_frame)
        self.cf_button_output.setMinimumSize(QSize(120, 35))
        self.cf_button_grid_layout.addWidget(self.cf_button_output, 0, 3)

        self.cf_button_copy.clicked.connect(self.call_copy_files)
        self.cf_button_output.clicked.connect(self.open_file_folder)
        self.cf_button_delete.clicked.connect(self.delete_files)
        self.cf_button_log.clicked.connect(self.view_log)

        self.cf_text_output.setPlaceholderText('Bienvenido a CopyFiles\nFuncionamiento: Inserta en la parte superior la ruta de los archivos que deseas copiar, en la parte inferior se mostrará el resultado de la operación.\n\nBotón Copiar: Inicia la copia de los archivos\nBotón Abrir Destino: Abre la carpeta de destino\nBotón Vaciar Destino: Elimina todos los archivos de la carpeta de destino\nBotón Ver Log: Abre el archivo de log\n\nNota: Si deseas cambiar el número de hilos, modifica el valor en el campo correspondiente y presiona el botón Copiar\n\nDado que el volumen de archivos a copiar puede ser grande, se recomienda usar un número de hilos mayor a 1 para acelerar el proceso. Y eliminarlos una vez finalizadas las acciones a realizar con ellos ya que se está trabajando con una carpeta compartida con todo el equipo\n\n')

    def search_in_local_buttons(self):
        """Elimina los widgets existentes y genera un nuevo botón y un campo de texto dentro de cf_variable_button_frame."""

        # 🔹 Verificar si cf_variable_button_frame ya tiene un layout
        if self.cf_variable_button_frame.layout() is None:
            self.cf_button_grid_layout = QGridLayout()  # Crear el layout
            self.cf_variable_button_frame.setLayout(self.cf_button_grid_layout)  # Asignarlo al frame
        else:
            self.cf_button_grid_layout = self.cf_variable_button_frame.layout()

            # 🔹 Si el layout ya existía, eliminar los widgets antiguos
            while self.cf_button_grid_layout.count():
                item = self.cf_button_grid_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

        # 🔹 Crear y agregar un campo de texto al layout dinámico
        # Define el diccionario con las opciones
        self.logical_operators_dict = {
            "AND": "AND",
            "OR": "OR",
            "NOT": "NOT",
            "XOR": "XOR",
            "NAND": "NAND",
            "NOR": "NOR"
        }

        # Crear el QComboBox y añadir las opciones del diccionario
        self.cf_logical_operators_combo = QComboBox(self.cf_variable_button_frame)
        self.cf_logical_operators_combo.setMinimumSize(QSize(200, 35))
        for key in self.logical_operators_dict.keys():
            self.cf_logical_operators_combo.addItem(key)
        self.cf_button_grid_layout.addWidget(self.cf_logical_operators_combo, 0, 0)

        self.cf_logical_operators_combo.setCurrentIndex(0)

        # 🔹 Crear y agregar un botón al layout dinámico
        self.cf_submit_button = QPushButton("Buscar", self.cf_variable_button_frame)
        self.cf_submit_button.setMinimumSize(QSize(120, 35))
        self.cf_button_grid_layout.addWidget(self.cf_submit_button, 0, 1)

        self.cf_button_output = QPushButton("Abrir Destino", self.cf_variable_button_frame)
        self.cf_button_output.setMinimumSize(QSize(120, 35))
        self.cf_button_grid_layout.addWidget(self.cf_button_output, 0, 3)


        self.cf_submit_button.clicked.connect(self.search_in_files)
        self.cf_button_output.clicked.connect(self.open_file_folder)


        self.cf_text_output.setPlaceholderText('Inserta la lista de caracteres a buscar con formato: \n\n Linea 1\n Linea 2\n Linea 3\n\n\nE inserta uno de los operadores logicos en el input destinado a ello.')


    def init_labels(self):
        self.cf_label_name = QLabel(self.frame)
        self.cf_label_name.setObjectName(u"cf_label_name")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.cf_label_name.sizePolicy().hasHeightForWidth())
        self.cf_label_name.setSizePolicy(sizePolicy1)
        self.cf_label_name.setMinimumSize(QSize(850, 100))
        self.cf_label_name.setMaximumSize(QSize(16777215, 100))
        self.cf_label_name.setAlignment(Qt.AlignCenter)
        self.cf_inner_grid_layout.addWidget(self.cf_label_name, 0, 0, 1, 4)

        self.cf_label_output = QLabel(self.frame)
        self.cf_label_output.setObjectName(u"cf_label_output")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cf_label_output.sizePolicy().hasHeightForWidth())
        self.cf_label_output.setSizePolicy(sizePolicy2)
        self.cf_label_output.setMinimumSize(QSize(850, 100))
        self.cf_label_output.setMaximumSize(QSize(16777215, 100))
        self.cf_label_output.setAlignment(Qt.AlignCenter)
        self.cf_inner_grid_layout.addWidget(self.cf_label_output, 7, 0, 1, 4)

        self.cf_threads_label = QLabel(self.frame)
        self.cf_threads_label.setObjectName(u"cf_threads_label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.cf_threads_label.sizePolicy().hasHeightForWidth())
        self.cf_threads_label.setSizePolicy(sizePolicy2)
        self.cf_threads_label.setMinimumSize(QSize(850, 100))
        self.cf_threads_label.setMaximumSize(QSize(16777215, 100))
        self.cf_threads_label.setAlignment(Qt.AlignCenter)
        self.cf_inner_grid_layout.addWidget(self.cf_threads_label, 6, 0, 1, 1)

    def init_text_inputs(self):
        self.cf_text_input = QTextEdit(self.frame)
        self.cf_text_input.setObjectName(u"cf_text_input")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(1)
        sizePolicy3.setHeightForWidth(self.cf_text_input.sizePolicy().hasHeightForWidth())
        self.cf_text_input.setSizePolicy(sizePolicy3)
        self.cf_inner_grid_layout.addWidget(self.cf_text_input, 1, 0, 1, 4)



        self.cf_integer_input = QLineEdit(self.frame)
        self.cf_integer_input.setObjectName(u"cf_integer_input")
        self.cf_integer_input.setValidator(QIntValidator())
        sizePolicy4 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(1)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.cf_integer_input.sizePolicy().hasHeightForWidth())
        self.cf_integer_input.setSizePolicy(sizePolicy4)
        self.cf_inner_grid_layout.addWidget(self.cf_integer_input, 6, 1, 1, 1)


    def init_progress_bar(self):
        self.cf_progress_bar = QProgressBar(self.frame)
        self.cf_progress_bar.setObjectName(u"cf_progress_bar")
        self.cf_progress_bar.setValue(0)
        self.cf_progress_bar.hide()
        self.cf_inner_grid_layout.addWidget(self.cf_progress_bar, 7, 0, 1, 4)

        self.cf_text_output = QTextEdit(self.frame)
        self.cf_text_output.setObjectName(u"cf_text_output")
        self.cf_inner_grid_layout.addWidget(self.cf_text_output, 8, 0, 1, 4)

    def retranslateUi(self, Form):
        self.setWindowTitle(QCoreApplication.translate("self", u"Copyfiles", None))
        self.cf_button_delete.setText(QCoreApplication.translate("self", u"Vaciar Destino", None))
        self.cf_button_copy.setText(QCoreApplication.translate("self", u"Copiar", None))
        self.cf_label_name.setText(QCoreApplication.translate("self", u"CopyFiles", None))
        self.cf_button_log.setText(QCoreApplication.translate("self", u"Ver Log", None))
        self.cf_label_output.setText(QCoreApplication.translate("self", u"Salida", None))
        self.cf_button_output.setText(QCoreApplication.translate("self", u"Abrir Destino", None))
        self.cf_threads_label.setText(QCoreApplication.translate("self", u"Numero de Hilos", None))
        self.cf_copy_files_button.setText(QCoreApplication.translate("self", u"Copiar Archivos", None))
        self.cf_search_local_button.setText(QCoreApplication.translate("self", u"Buscar Local", None))

    # retranslateUi

    def search_in_files(self):
        self.test_paths()

        input_search = [line.strip() for line in self.cf_text_input.toPlainText().splitlines() if line.strip()]
        logical_operators = self.logical_operators_dict[self.cf_logical_operators_combo.currentText()]
        files = []

        for root, dirs, filenames in os.walk(self.path_to_files):
            for filename in filenames:
                files.append(os.path.join(root, filename))

        self.cf_progress_bar.setValue(0)  # Reset progress bar
        self.cf_progress_bar.show()

        threads = int(self.cf_integer_input.text())

        batches = [files[i::threads] for i in range(threads)]  # Usar el valor de threads en lugar de 4
        self.threads = []
        self.total_success = 0  # Resetear el contador de archivos copiados
        self.threads_finished = 0  # Inicializar el contador de hilos terminados
        self.total_fail = 0  # Inicializar el contador de fallos

        for batch in batches:
            thread = SearchFilesThread(batch, self.path_to_files, self.path_to_log, self.path_to_found, input_search, logical_operators)
            thread.update_progress.connect(self.update_progress)
            thread.finished_searching.connect(self.update_total_success)
            thread.start()
            self.threads.append(thread)


    def call_copy_files(self):
        self.test_paths()

        #files = [line.strip() for line in self.cf_text_input.toPlainText().splitlines() if line.strip()]

        input_paths = [line.strip() for line in self.cf_text_input.toPlainText().splitlines() if line.strip()]

        files = []
        directories = []

        for path in input_paths:
            if os.path.isfile(path):
                files.append(path)
            elif os.path.isdir(path):
                directories.append(path)

        # Extraer la ruta absoluta de todos los archivos en los directorios
        for directory in directories:
            for root, _, filenames in os.walk(directory):
                for filename in filenames:
                    files.append(os.path.join(root, filename))



        self.cf_progress_bar.setValue(0)  # Reset progress bar
        self.cf_progress_bar.show()

        threads = int(self.cf_integer_input.text())

        batches = [files[i::threads] for i in range(threads)]  # Usar el valor de threads en lugar de 4
        self.threads = []
        self.total_success = 0  # Resetear el contador de archivos copiados
        self.threads_finished = 0  # Inicializar el contador de hilos terminados
        self.total_fail = 0  # Inicializar el contador de fallos

        for batch in batches:
            thread = CopyFilesThread(batch, self.path_to_files, self.path_to_log)
            thread.update_progress.connect(self.update_progress)
            thread.finished_copying.connect(self.update_total_success)
            thread.start()
            self.threads.append(thread)

    def update_progress(self, progress):
        self.cf_progress_bar.setValue(progress)

    def update_total_success(self, success, fail):
        self.total_success += success
        self.total_fail += fail  # Añadir un contador de fallos
        self.threads_finished += 1
        if self.threads_finished == len(self.threads):  # Verificar si todos los hilos han terminado
            success_message = f"Copiados {self.total_success} archivos correctamente"
            self.show_results(success_message)
            if self.total_fail > 0:
                fail_message = f"{self.total_fail} archivos fallidos. Revisar {self.path_to_log}"
                self.show_results(fail_message)

    def test_paths(self):
        if not os.path.exists(self.path_to_files):
            os.makedirs(self.path_to_files, exist_ok=True)
        if not os.path.exists(self.path_to_log):
            os.makedirs(os.path.dirname(self.path_to_log), exist_ok=True)
        if not os.path.exists(self.path_to_found):
            os.makedirs(self.path_to_found, exist_ok=True)  # Crear el directorio directamente

    def show_results(self, text):
        self.cf_text_output.setReadOnly(False)
        self.cf_text_output.append(text)
        self.cf_text_output.setReadOnly(True)

    def remove_component(self, component):
        if component in self.cf_inner_grid_layout:
            widget = self.cf_inner_grid_layout.itemAt(component).widget()
            if widget:
                widget.deleteLater()
                self.cf_inner_grid_layout.removeWidget(widget)


    def open_file_folder(self):
        if not os.path.exists(self.path_to_files):
            os.mkdir(self.path_to_files)
        if os.name == 'nt':  # Windows
            os.system(f'start explorer {self.path_to_files}')
        else:  # Linux
            os.system(f'xdg-open {self.path_to_files}')

    def view_log(self):
        if os.name == 'nt':  # Windows
            os.system(f'start notepad.exe {self.path_to_log}')
        else:  # Linux
            os.system(f'kate  {self.path_to_log} &')

    def delete_files(self):
        cont = 0;
        fail = 0;
        for filename in os.listdir(self.path_to_files):
            file_path = os.path.join(self.path_to_files, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    cont += 1
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    cont += 1
            except Exception as e:
                self.show_results(f"No se pudo eliminar {file_path} debido a {e}")
                fail += 1
        self.show_results( f'Eliminados {cont} archivos y carpetas correctamente. Fallo en {fail} elementos.')

def load_stylesheet(app, path):
    with open(path, "r") as file:
        qss = file.read()
        app.setStyleSheet(qss)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    load_stylesheet(app, "Combinear.qss")
    window = CopyFiles()
    window.show()
    sys.exit(app.exec_())
