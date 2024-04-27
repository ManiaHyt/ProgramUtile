import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QComboBox, QMessageBox
from PyQt5.QtCore import pyqtSlot
from YoutubeDownloaderFunctions import download_video, list_all_resolutions, ensure_directory_exists, validate_timecode, download_audio
from pytube import YouTube

class YoutubeDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()

        # Configuration des éléments de l'interface utilisateur
        self.setupUIElements(layout)

        # Widget central
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def setupUIElements(self, layout):
        self.url_label = QLabel("URL de la vidéo:")
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Entrez l'URL de la vidéo YouTube ici")
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)

        self.validate_button = QPushButton("Valider l'URL", self)
        self.validate_button.clicked.connect(self.validate_url)
        layout.addWidget(self.validate_button)

        self.full_video_radio = QRadioButton("Télécharger vidéo entière")
        self.part_video_radio = QRadioButton("Télécharger un extrait")
        self.full_video_radio.setChecked(True)
        layout.addWidget(self.full_video_radio)
        layout.addWidget(self.part_video_radio)

        self.start_time_label = QLabel("Timecode de début (hh:mm:ss):")
        self.start_time_input = QLineEdit(self)
        self.start_time_input.setDisabled(True)
        self.end_time_label = QLabel("Timecode de fin (hh:mm:ss):")
        self.end_time_input = QLineEdit(self)
        self.end_time_input.setDisabled(True)
        layout.addWidget(self.start_time_label)
        layout.addWidget(self.start_time_input)
        layout.addWidget(self.end_time_label)
        layout.addWidget(self.end_time_input)

        self.part_video_radio.toggled.connect(self.on_radio_button_toggled)

        self.resolution_label = QLabel("Sélectionnez la qualité de la vidéo:")
        self.resolution_combobox = QComboBox(self)
        self.resolution_combobox.setDisabled(True)
        layout.addWidget(self.resolution_label)
        layout.addWidget(self.resolution_combobox)

        self.download_button = QPushButton("Télécharger la vidéo", self)
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button)

        # Bouton pour télécharger uniquement l'audio
        self.download_audio_button = QPushButton("Télécharger l'audio", self)
        self.download_audio_button.clicked.connect(self.download_audio)
        layout.addWidget(self.download_audio_button)

    @pyqtSlot()
    def download_audio(self):
        url = self.url_input.text()
        if url:
            output_folder = ensure_directory_exists("Downloads")
            audio_path = download_audio(url, output_folder)
            if audio_path:
                QMessageBox.information(self, "Téléchargement", "L'audio a été téléchargé avec succès.")
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de télécharger l'audio.")
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")

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
        url = self.url_input.text()
        if url:
            yt = YouTube(url)
            resolutions = list_all_resolutions(yt)
            self.resolution_combobox.clear()
            self.resolution_combobox.addItems(resolutions)
            self.resolution_combobox.setEnabled(True)
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")

    def download_video(self):
        url = self.url_input.text()
        start_time = self.start_time_input.text() if self.start_time_input.isEnabled() else None
        end_time = self.end_time_input.text() if self.end_time_input.isEnabled() else None
        resolution = self.resolution_combobox.currentText()
        full_video = self.full_video_radio.isChecked()

        if url and (full_video or (validate_timecode(start_time) and validate_timecode(end_time))):
            output_folder = ensure_directory_exists("Downloads")
            download_video(url, output_folder, resolution, full_video, start_time, end_time)
            QMessageBox.information(self, "Téléchargement", "La vidéo a été téléchargée avec succès.")
        else:
            QMessageBox.warning(self, "Erreur", "Veuillez remplir correctement tous les champs requis.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = YoutubeDownloaderGUI()
    ex.show()
    sys.exit(app.exec_())
