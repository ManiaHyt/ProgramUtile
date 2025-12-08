from pytubefix import YouTube
from moviepy import VideoFileClip, AudioFileClip
import os
import re

# Vérification et création du répertoire si nécessaire
def ensure_directory_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


# Obtenir la liste des résolutions disponibles pour une vidéo YouTube
def list_all_resolutions(yt):
    streams = yt.streams.filter(mime_type="video/mp4").order_by("resolution").desc()
    unique_resolutions = sorted(
        {stream.resolution for stream in streams if stream.resolution},
        reverse=True,
    )
    return unique_resolutions


# Validation du format de timecode
def validate_timecode(timecode):
    return bool(re.match(r"^\d{2}:\d{2}:\d{2}$", timecode))


# Nettoyage du titre de la vidéo pour les noms de fichiers
def clean_title(title):
    return re.sub(r'[\\/:*?"<>|]', "_", title)


def timecode_to_seconds(tc: str) -> int:
    """Convertit un timecode 'hh:mm:ss' en secondes."""
    h, m, s = map(int, tc.split(":"))
    return h * 3600 + m * 60 + s


def download_video(url, output_folder, resolution=None, full_video=True, start_time=None, end_time=None):
    try:
        yt = YouTube(url)
        title = clean_title(yt.title)

        # --- CAS 1 : téléchargement de la vidéo complète ---
        if full_video:
            stream = yt.streams.filter(
                res=resolution,
                mime_type="video/mp4",
                progressive=True
            ).first()

            if not stream:
                stream = yt.streams.filter(
                    res=resolution,
                    file_extension="mp4",
                    progressive=True
                ).first()

            if not stream:
                print("Aucun flux vidéo progressif trouvé pour cette résolution.")
                return None

            # Chemin réel retourné par pytube
            download_path = stream.download(
                output_path=output_folder,
                filename=f"{title}.mp4"
            )
            print("Vidéo complète téléchargée :", download_path)
            return download_path

        # --- CAS 2 : téléchargement d'un extrait ---
        # On suppose que start_time et end_time ont été validés avant (format hh:mm:ss)
        if not (start_time and end_time):
            raise ValueError("Les timecodes de début et de fin doivent être fournis pour un extrait.")

        start_sec = timecode_to_seconds(start_time)
        end_sec = timecode_to_seconds(end_time)

        if end_sec <= start_sec:
            raise ValueError("Le timecode de fin doit être supérieur au timecode de début.")

        # Flux vidéo seul
        video_stream = yt.streams.filter(
            res=resolution,
            mime_type="video/mp4",
            only_video=True
        ).first()

        if not video_stream:
            video_stream = yt.streams.filter(
                res=resolution,
                file_extension="mp4",
                only_video=True
            ).first()

        # Flux audio seul
        audio_stream = yt.streams.filter(only_audio=True).first()

        if not video_stream or not audio_stream:
            print("Flux vidéo ou audio manquant pour créer l'extrait.")
            return None

        # On laisse pytube choisir exactement le chemin, et on récupère ce chemin
        video_temp_path = video_stream.download(
            output_path=output_folder,
            filename=f"{title}_video"
        )
        audio_temp_path = audio_stream.download(
            output_path=output_folder,
            filename=f"{title}_audio"
        )

        print("Vidéo temporaire :", video_temp_path)
        print("Audio temporaire :", audio_temp_path)

        # Fusion vidéo + audio
        video_clip = VideoFileClip(video_temp_path)
        audio_clip = AudioFileClip(audio_temp_path)
        final_clip = video_clip.with_audio(audio_clip).subclipped(start_sec, end_sec)

        final_path = os.path.join(output_folder, f"{title}.mp4")
        final_clip.write_videofile(final_path, codec="libx264")

        # Fermeture des clips
        video_clip.close()
        audio_clip.close()
        final_clip.close()

        # Nettoyage des fichiers temporaires
        for temp_path in (video_temp_path, audio_temp_path):
            try:
                os.remove(temp_path)
            except FileNotFoundError:
                pass

        print("Extrait vidéo créé :", final_path)
        return final_path

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

        # On laisse pytube gérer l'extension réelle ; ici on force juste le nom
        audio_path = audio_stream.download(
            output_path=output_folder,
            filename=f"{title}.mp3"
        )
        print("Audio téléchargé :", audio_path)
        return audio_path

    except Exception as e:
        print(f"Erreur lors du téléchargement de l'audio : {e}")
        return None
