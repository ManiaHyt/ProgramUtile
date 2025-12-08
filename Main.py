import sys
import os

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QComboBox,
    QMessageBox,
    QTabWidget,
    QFileDialog,
    QAction,
)
from PyQt5.QtCore import pyqtSlot

from pytubefix import YouTube
from YoutubeDownloaderFunctions import (
    download_video,
    list_all_resolutions,
    ensure_directory_exists,
    validate_timecode,
    download_audio,
)

from PIL import Image  # pour la conversion d’images


# ---------------------------
# Onglet 1 : Downloader YouTube
# ---------------------------
class YoutubeDownloaderTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # URL
        self.url_label = QLabel("URL de la vidéo :")
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Entrez l'URL de la vidéo YouTube ici")
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        # Bouton de validation
        self.validate_button = QPushButton("Valider l'URL", self)
        self.validate_button.clicked.connect(self.validate_url)
        layout.addWidget(self.validate_button)

        # Choix vidéo entière / extrait
        self.full_video_radio = QRadioButton("Télécharger vidéo entière")
        self.part_video_radio = QRadioButton("Télécharger un extrait")
        self.full_video_radio.setChecked(True)
        layout.addWidget(self.full_video_radio)
        layout.addWidget(self.part_video_radio)

        # Timecodes
        self.start_time_label = QLabel("Timecode de début (hh:mm:ss) :")
        self.start_time_input = QLineEdit(self)
        self.start_time_input.setDisabled(True)

        self.end_time_label = QLabel("Timecode de fin (hh:mm:ss) :")
        self.end_time_input = QLineEdit(self)
        self.end_time_input.setDisabled(True)

        layout.addWidget(self.start_time_label)
        layout.addWidget(self.start_time_input)
        layout.addWidget(self.end_time_label)
        layout.addWidget(self.end_time_input)

        self.part_video_radio.toggled.connect(self.on_radio_button_toggled)

        # Résolution
        self.resolution_label = QLabel("Sélectionnez la qualité de la vidéo :")
        self.resolution_combobox = QComboBox(self)
        self.resolution_combobox.setDisabled(True)
        layout.addWidget(self.resolution_label)
        layout.addWidget(self.resolution_combobox)

        # Bouton téléchargement vidéo
        self.download_button = QPushButton("Télécharger la vidéo", self)
        self.download_button.clicked.connect(self.download_video_slot)
        layout.addWidget(self.download_button)

        # Bouton téléchargement audio
        self.download_audio_button = QPushButton("Télécharger l'audio", self)
        self.download_audio_button.clicked.connect(self.download_audio_slot)
        layout.addWidget(self.download_audio_button)

        self.setLayout(layout)

    @pyqtSlot()
    def on_radio_button_toggled(self):
        if self.part_video_radio.isChecked():
            self.start_time_input.setEnabled(True)
            self.end_time_input.setEnabled(True)
        else:
            self.start_time_input.setDisabled(True)
            self.end_time_input.setDisabled(True)

    @pyqtSlot()
    def validate_url(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")
            return

        try:
            yt = YouTube(url)
            yt.check_availability()  # lève une exception si la vidéo n’est pas accessible

            resolutions = list_all_resolutions(yt)
            self.resolution_combobox.clear()
            self.resolution_combobox.addItems(resolutions)
            self.resolution_combobox.setEnabled(True)

            QMessageBox.information(
                self,
                "Succès",
                "URL validée. Vous pouvez maintenant sélectionner une résolution.",
            )
        except Exception as e:
            self.resolution_combobox.clear()
            self.resolution_combobox.setDisabled(True)
            QMessageBox.critical(
                self,
                "Erreur de validation",
                f"L'URL est invalide ou la vidéo n'est pas accessible.\nErreur : {e}",
            )

    @pyqtSlot()
    def download_video_slot(self):
        url = self.url_input.text().strip()
        start_time = self.start_time_input.text().strip() if self.start_time_input.isEnabled() else None
        end_time = self.end_time_input.text().strip() if self.end_time_input.isEnabled() else None
        resolution = self.resolution_combobox.currentText()

        is_full_video = self.full_video_radio.isChecked()
        is_valid_clip = (
            not is_full_video
            and start_time
            and end_time
            and validate_timecode(start_time)
            and validate_timecode(end_time)
        )

        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL.")
            return

        if not (is_full_video or is_valid_clip):
            QMessageBox.warning(
                self,
                "Erreur",
                "Veuillez remplir correctement les timecodes (format hh:mm:ss) ou choisir vidéo entière.",
            )
            return

        output_folder = ensure_directory_exists("Downloads")
        try:
            path = download_video(url, output_folder, resolution, is_full_video, start_time, end_time)
            if path and os.path.exists(path):
                QMessageBox.information(
                    self,
                    "Téléchargement",
                    f"La vidéo a été téléchargée avec succès.\nEmplacement : {path}",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Téléchargement",
                    "Le téléchargement semble avoir échoué (aucun fichier généré).",
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur de téléchargement",
                f"Une erreur est survenue lors du téléchargement.\nErreur : {e}",
            )

    @pyqtSlot()
    def download_audio_slot(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")
            return

        output_folder = ensure_directory_exists("Downloads")
        audio_path = download_audio(url, output_folder)
        if audio_path and os.path.exists(audio_path):
            QMessageBox.information(
                self,
                "Téléchargement",
                f"L'audio a été téléchargé avec succès.\nEmplacement : {audio_path}",
            )
        else:
            QMessageBox.warning(
                self,
                "Erreur",
                "Impossible de télécharger l'audio.",
            )


# ---------------------------
# Onglet 2 : Convertisseur d’images (WebP -> PNG/JPEG)
# ---------------------------
class ImageConverterTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Zone de sélection de fichier
        self.path_label = QLabel("Aucun fichier sélectionné.")
        self.select_button = QPushButton("Sélectionner une image WebP")
        self.select_button.clicked.connect(self.select_file)

        layout.addWidget(self.path_label)
        layout.addWidget(self.select_button)

        # Choix du format de sortie
        format_layout = QHBoxLayout()
        format_label = QLabel("Format de sortie :")
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(["png", "jpeg"])

        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combobox)
        layout.addLayout(format_layout)

        # Bouton de conversion
        self.convert_button = QPushButton("Convertir l'image")
        self.convert_button.clicked.connect(self.convert_image)
        layout.addWidget(self.convert_button)

        self.setLayout(layout)

    @pyqtSlot()
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image WebP",
            "",
            "Images WebP (*.webp);;Tous les fichiers (*.*)",
        )
        if file_path:
            self.file_path = file_path
            self.path_label.setText(f"Fichier sélectionné : {file_path}")
        else:
            self.file_path = None
            self.path_label.setText("Aucun fichier sélectionné.")

    @pyqtSlot()
    def convert_image(self):
        if not self.file_path:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un fichier WebP.")
            return

        output_format = self.format_combobox.currentText()  # "png" ou "jpeg"
        try:
            img = Image.open(self.file_path)

            base, _ = os.path.splitext(self.file_path)
            output_path = f"{base}.{output_format}"

            # Si l'image a un canal alpha et qu'on convertit en JPEG, on peut gérer ça :
            if output_format == "jpeg" and img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # masque = alpha
                background.save(output_path, output_format.upper())
            else:
                img.save(output_path, output_format.upper())

            QMessageBox.information(
                self,
                "Conversion terminée",
                f"Image convertie et sauvegardée sous :\n{output_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur de conversion",
                f"Une erreur est survenue lors de la conversion :\n{e}",
            )


# ---------------------------
# Fenêtre principale avec menu + onglets
# ---------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Outils multimédia")
        self.setGeometry(100, 100, 600, 400)

        # --- Barre de menus ---
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Fichier")

        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # --- Onglets ---
        tabs = QTabWidget()
        tabs.addTab(YoutubeDownloaderTab(self), "Télécharger des vidéos")
        tabs.addTab(ImageConverterTab(self), "Convertir des images")

        self.setCentralWidget(tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
