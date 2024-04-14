from pytube import YouTube
from moviepy.editor import VideoFileClip
import os


def ensure_directory_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def download_video(url, output_folder, full_video=True, start_time=None, end_time=None):
    yt = YouTube(url)
    ys = yt.streams.get_highest_resolution()

    print("Téléchargement en cours...")
    output_folder = ensure_directory_exists(output_folder)
    file_path = ys.download(output_path=output_folder)
    print("Téléchargement terminé.")

    if not full_video:
        if start_time is not None and end_time is not None:
            clip = VideoFileClip(file_path).subclip(start_time, end_time)
            new_file_name = os.path.splitext(os.path.basename(file_path))[0] + "_clip.mp4"
            new_file_path = os.path.join(output_folder, new_file_name)
            clip.write_videofile(new_file_path, codec='libx264')
            clip.close()  # Ferme explicitement le clip pour libérer le fichier original
            os.remove(file_path)  # Supprime le fichier original après fermeture de tous les processus
            print(f"Extrait enregistré sous : {new_file_path}")
        else:
            print("Les timecodes fournis sont invalides.")
    else:
        print(f"Vidéo complète enregistrée sous : {file_path}")


def main():
    output_folder = "media"  # Nom du dossier de destination
    url = input("Entrez l'URL de la vidéo YouTube : ")
    choice = input("Voulez-vous télécharger la vidéo entière ou juste un extrait ? (entière/extrait) : ").lower()

    if choice == 'extrait':
        start_time = input("Entrez le timecode de début (format hh:mm:ss) : ")
        end_time = input("Entrez le timecode de fin (format hh:mm:ss) : ")
        download_video(url, output_folder, full_video=False, start_time=start_time, end_time=end_time)
    elif choice == 'entière':
        download_video(url, output_folder)
    else:
        print("Choix non reconnu.")


if __name__ == "__main__":
    main()
