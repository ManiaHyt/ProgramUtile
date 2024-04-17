from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip
import os
import re

def ensure_directory_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def list_available_resolutions(yt):
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution')
    unique_resolutions = sorted(set([stream.resolution for stream in streams if stream.resolution]), reverse=True)
    return unique_resolutions

def validate_timecode(timecode):
    if re.match(r'^\d{2}:\d{2}:\d{2}$', timecode):
        return True
    return False

def clean_title(title):
    # Nettoie le titre pour l'utiliser comme nom de fichier en éliminant les caractères problématiques
    return re.sub(r'[\/:*?"<>|\\]', '_', title)

def download_and_merge_video(url, output_folder, resolution=None, full_video=True, start_time=None, end_time=None):
    yt = YouTube(url)
    available_resolutions = list_available_resolutions(yt)
    if resolution not in available_resolutions:
        print("Résolution non disponible. Voici les options disponibles:")
        for res in available_resolutions:
            print(res)
        return

    video_stream = yt.streams.filter(resolution=resolution, mime_type='video/mp4').order_by('resolution').desc().first()
    audio_stream = yt.streams.filter(only_audio=True, mime_type='audio/mp4').desc().first()

    print("Téléchargement en cours...")
    output_folder = ensure_directory_exists(output_folder)
    video_file_path = video_stream.download(output_path=output_folder, filename_prefix='video_')
    audio_file_path = audio_stream.download(output_path=output_folder, filename_prefix='audio_')

    print("Téléchargement terminé. Traitement en cours...")
    try:
        final_video = VideoFileClip(video_file_path)
        final_audio = AudioFileClip(audio_file_path)
        final_video = final_video.set_audio(final_audio)

        if not full_video and validate_timecode(start_time) and validate_timecode(end_time):
            final_video = final_video.subclip(start_time, end_time)

        sanitized_title = clean_title(yt.title)
        final_file_path = os.path.join(output_folder, f"{sanitized_title}_final.mp4")
        final_video.write_videofile(final_file_path, codec='libx264', temp_audiofile='temp-audio.m4a', remove_temp=True, audio_codec='aac')
        final_video.close()
        final_audio.close()

        print(f"Vidéo sauvegardée sous : {final_file_path}")
    except Exception as e:
        print(f"Erreur lors de la création de la vidéo : {e}")
    finally:
        if os.path.exists(video_file_path):
            os.remove(video_file_path)
        if os.path.exists(audio_file_path):
            os.remove(audio_file_path)

def main():
    output_folder = "media"
    while True:
        url = input("Entrez l'URL de la vidéo YouTube ou tapez 'exit' pour quitter : ")
        if url.lower() == 'exit':
            break

        try:
            yt = YouTube(url)
        except Exception as e:
            print(f"Erreur lors de la récupération de la vidéo : {e}")
            continue

        available_resolutions = list_available_resolutions(yt)
        print("Résolutions disponibles :")
        for res in available_resolutions:
            print(res)
        resolution = input("Choisissez une résolution parmi les options ci-dessus : ")

        if resolution not in available_resolutions:
            print("Résolution non reconnue. Veuillez essayer à nouveau.")
            continue

        choice = input("Voulez-vous télécharger la vidéo entière ou juste un extrait ? (entière/extrait) : ").lower()

        if choice == 'extrait':
            start_time = input("Entrez le timecode de début (format hh:mm:ss) : ")
            end_time = input("Entrez le timecode de fin (format hh:mm:ss) : ")
            download_and_merge_video(url, output_folder, resolution, full_video=False, start_time=start_time, end_time=end_time)
        elif choice == 'entière':
            download_and_merge_video(url, output_folder, resolution)
        else:
            print("Choix non reconnu. Veuillez essayer à nouveau.")

if __name__ == "__main__":
    main()
