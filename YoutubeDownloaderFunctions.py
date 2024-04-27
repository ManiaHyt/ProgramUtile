from moviepy.audio.io.AudioFileClip import AudioFileClip
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os
import re


# Vérification et création du répertoire si nécessaire
def ensure_directory_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


# Obtenir la liste des résolutions disponibles pour une vidéo YouTube
def list_all_resolutions(yt):
    streams = yt.streams.filter(mime_type='video/mp4').order_by('resolution').desc()
    unique_resolutions = sorted(set([stream.resolution for stream in streams if stream.resolution]), reverse=True)
    return unique_resolutions


# Validation du format de timecode
def validate_timecode(timecode):
    return bool(re.match(r'^\d{2}:\d{2}:\d{2}$', timecode))


# Nettoyage du titre de la vidéo pour les noms de fichiers
def clean_title(title):
    return re.sub(r'[\\/:*?"<>|]', '_', title)


# Téléchargement de la vidéo avec options de résolution et extrait spécifique
def clean_title(title):
    return re.sub(r'[\\/:*?"<>|]', '_', title)


def clean_title(title):
    return re.sub(r'[\\/:*?"<>|]', '_', title)


def download_video(url, output_folder, resolution=None, full_video=True, start_time=None, end_time=None):
    try:
        yt = YouTube(url)
        title = clean_title(yt.title)
        file_path = os.path.join(output_folder, f"{title}.mp4")  # Assure que le chemin du fichier final est en .mp4

        if full_video:
            video_stream = yt.streams.filter(res=resolution, mime_type='video/mp4', progressive=True).first()
            if not video_stream:
                print("Aucun flux vidéo progressif trouvé.")
                return None
            video_stream.download(output_folder, filename=title + ".mp4")
        else:
            video_stream = yt.streams.filter(res=resolution, mime_type='video/mp4', only_video=True).first()
            audio_stream = yt.streams.filter(only_audio=True).first()
            if not video_stream or not audio_stream:
                print("Flux vidéo ou audio manquant.")
                return None

            video_path = os.path.join(output_folder, f"{title}_video.mp4")
            audio_path = os.path.join(output_folder, f"{title}_audio.mp4")
            video_stream.download(output_folder, filename=f"{title}_video")
            audio_stream.download(output_folder, filename=f"{title}_audio")

            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)
            final_clip = video_clip.set_audio(audio_clip)

            if start_time and end_time:
                final_clip = final_clip.subclip(start_time, end_time)

            final_clip.write_videofile(file_path,
                                       codec="libx264")  # Spécifie le codec pour s'assurer que la sortie est en MP4

            os.remove(video_path)
            os.remove(audio_path)
        return file_path
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")
        return None

def download_audio(url, output_folder):
    try:
        yt = YouTube(url)
        title = clean_title(yt.title)
        audio_stream = yt.streams.filter(only_audio=True).first()
        if not audio_stream:
            print("Aucun flux audio trouvé.")
            return None

        audio_path = os.path.join(output_folder, f"{title}.mp3")  # Sauvegarde en .mp3
        audio_stream.download(output_folder, filename=f"{title}.mp3")
        return audio_path
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'audio : {e}")
        return None