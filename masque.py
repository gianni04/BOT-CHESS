import mss
import cv2
import numpy as np
import os

DOSSIER_PROJET = r"C:\Users\giann\OneDrive\Bureau\IA chess\v2"
os.chdir(DOSSIER_PROJET)

ZONE_ECHIQUIER = {"top": 156, "left": 2315, "width": 805, "height": 799}

def main():
    print("🔍 Test du Filtre 'Tampon Encreur'...")
    with mss.mss() as sct:
        img = np.array(sct.grab(ZONE_ECHIQUIER))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    # 💥 LA MAGIE EST LÀ : On ne garde que les pixels très foncés (0 à 85)
    # Le vert et le beige vont être détruits.
    masque_noir = cv2.inRange(img_bgr, (0, 0, 0), (85, 85, 85))

    cv2.imwrite("debug_masque.png", masque_noir)
    print("✅ Fichier 'debug_masque.png' créé dans ton dossier !")

if __name__ == "__main__":
    main()