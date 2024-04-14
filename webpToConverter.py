from PIL import Image
import tkinter as tk
from tkinter import filedialog

def select_webp_image():
    root = tk.Tk()
    root.withdraw()  # Pour ne pas afficher la fenêtre principale de Tkinter
    file_path = filedialog.askopenfilename(filetypes=[("WebP files", "*.webp")])
    if file_path:
        return file_path
    else:
        print("Aucun fichier sélectionné.")
        return None

def convert_image(file_path, output_format):
    img = Image.open(file_path)
    output_path = file_path.rsplit('.', 1)[0] + output_format
    img.save(output_path)
    print(f"Image convertie et sauvegardée sous : {output_path}")

def main():
    print("Sélectionnez un fichier image WebP.")
    file_path = select_webp_image()
    if file_path:
        print("Formats de sortie disponibles: .png, .jpeg")
        output_format = input("Entrez le format de sortie souhaité (sans le point): ").strip()
        if output_format in ['png', 'jpeg']:
            convert_image(file_path, '.' + output_format)
        else:
            print("Format non supporté.")

if __name__ == "__main__":
    main()
