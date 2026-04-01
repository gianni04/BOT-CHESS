import mss
import cv2
import numpy as np
import os

DOSSIER_PROJET = r"C:\Users\giann\OneDrive\Bureau\IA chess\v2"
DOSSIER_TEMPLATES = os.path.join(DOSSIER_PROJET, "templates")
ZONE_ECHIQUIER = {"top": 156, "left": 2315, "width": 805, "height": 799}
TRADUCTION_FEN = {'bB':'b','bK':'k','bN':'n','bP':'p','bQ':'q','bR':'r','wB':'B','wK':'K','wN':'N','wP':'P','wQ':'Q','wR':'R'}

def main():
    print("🔍 Lancement du diagnostic 'Silhouette Épaisse'...")
    templates_contours = {}
    
    # 💥 L'ARME SECRÈTE : Un noyau 3x3 pour épaissir les lignes
    kernel = np.ones((3,3), np.uint8)

    for nom in TRADUCTION_FEN.keys():
        img = cv2.imread(os.path.join(DOSSIER_TEMPLATES, f"{nom}.png"), cv2.IMREAD_GRAYSCALE)
        
        # 1. On trouve les lignes fines (ignorant le fond vert/beige)
        canny = cv2.Canny(img, 50, 150)
        # 2. On épaissit les traits au "gros marqueur"
        canny_epais = cv2.dilate(canny, kernel, iterations=1)
        templates_contours[nom] = canny_epais

    with mss.mss() as sct:
        img = np.array(sct.grab(ZONE_ECHIQUIER))
        gris = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        
        # On fait pareil pour l'écran en direct
        ecran_canny = cv2.Canny(gris, 50, 150)
        ecran_canny_epais = cv2.dilate(ecran_canny, kernel, iterations=1)
    
    h, w = ecran_canny_epais.shape
    th, tl = h / 8, w / 8
    plateau = []
    scores = []

    for y in range(8):
        for x in range(8):
            y1, y2 = int(y * th), int((y + 1) * th)
            x1, x2 = int(x * tl), int((x + 1) * tl)
            case_contour = ecran_canny_epais[y1:y2, x1:x2]
            
            meilleur_score = 0
            meilleure_piece = '1'
            
            for nom, tmpl in templates_contours.items():
                res = cv2.matchTemplate(case_contour, tmpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > meilleur_score:
                    meilleur_score = max_val
                    meilleure_piece = nom
            
            # On stocke le score que si on a détecté une pièce (pour éviter de plomber la moyenne avec les cases vides)
            if meilleur_score > 0.15:
                scores.append(meilleur_score)
            
            # 35% de correspondance sur une forme épaisse suffit largement
            if meilleur_score > 0.35: 
                plateau.append(TRADUCTION_FEN[meilleure_piece])
            else:
                plateau.append('1')
    
    fen = ""
    for i in range(8):
        vide = 0
        for j in range(8):
            p = plateau[i*8+j]
            if p == '1': vide += 1
            else:
                if vide > 0: fen += str(vide); vide = 0
                fen += p
        if vide > 0: fen += str(vide)
        if i < 7: fen += "/"

    print("\n=========================================")
    print(f"👉 FEN DÉTECTÉ : {fen}")
    # Sécurité si le tableau scores est vide
    if len(scores) > 0:
        print(f"📊 Score moyen des pièces : {np.mean(scores):.2f}")
        print(f"📉 Min : {np.min(scores):.2f} | 📈 Max : {np.max(scores):.2f}")
    else:
        print("📊 Aucune pièce trouvée.")
    print("=========================================")

if __name__ == "__main__":
    main()