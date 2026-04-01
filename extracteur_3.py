import mss
import cv2
import numpy as np
import os

DOSSIER_PROJET = r"C:\Users\giann\OneDrive\Bureau\IA chess\v2"
DOSSIER_TEMPLATES = os.path.join(DOSSIER_PROJET, "templates")

if not os.path.exists(DOSSIER_TEMPLATES):
    os.makedirs(DOSSIER_TEMPLATES)

# TES NOUVELLES COORDONNÉES PARFAITES
ZONE_ECHIQUIER = {"top": 152, "left": 2157, "width": 807, "height": 806}

PIECES_A_EXTRAIRE = {
    'bR': (0, 0), 'bN': (0, 1), 'bB': (0, 2), 'bQ': (0, 3), 'bK': (0, 4), 'bP': (1, 0),
    'wP': (6, 0), 'wR': (7, 0), 'wN': (7, 1), 'wB': (7, 2), 'wQ': (7, 3), 'wK': (7, 4)
}

def main():
    print("📸 Capture et application du filtre optique...")
    with mss.mss() as sct:
        img = np.array(sct.grab(ZONE_ECHIQUIER))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) 

    # LE FILTRE : On isole les pixels foncés (les pièces deviennent blanches, le fond devient noir)
    masque = cv2.inRange(img_bgr, (0, 0, 0), (85, 85, 85))

    h, w = masque.shape
    taille_y = h / 8
    taille_x = w / 8

    print(f"📂 Sauvegarde des 12 nouvelles silhouettes dans : {DOSSIER_TEMPLATES}\n")

    for nom_piece, (lig, col) in PIECES_A_EXTRAIRE.items():
        y1, y2 = int(lig * taille_y), int((lig + 1) * taille_y)
        x1, x2 = int(col * taille_x), int((col + 1) * taille_x)
        
        # On rogne un peu les bords pour éviter les bavures des lignes de l'échiquier
        marge = 5
        case_img = masque[y1+marge : y2-marge, x1+marge : x2-marge]
        
        chemin_fichier = os.path.join(DOSSIER_TEMPLATES, f"{nom_piece}.png")
        cv2.imwrite(chemin_fichier, case_img)
        print(f"✅ Silhouette extraite : {nom_piece}.png")

    print("\n🚀 OPÉRATION TERMINÉE ! Vérifie ton dossier 'templates'.")

if __name__ == "__main__":
    main()