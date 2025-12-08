import os
import cairosvg

# Dossier contenant les fichiers SVG
input_folder = "assets"
# Dossier où les fichiers PNG seront enregistrés
output_folder = "assets/png"

# Créer le dossier de sortie s'il n'existe pas
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Parcourir tous les fichiers du dossier SVG
for filename in os.listdir(input_folder):
    if filename.endswith(".svg"):
        svg_path = os.path.join(input_folder, filename)
        png_filename = filename.replace(".svg", ".png")
        png_path = os.path.join(output_folder, png_filename)
        
        # Conversion SVG → PNG
        cairosvg.svg2png(url=svg_path, write_to=png_path)
        print(f"Converti : {filename} → {png_filename}")

print("Conversion terminée !")
