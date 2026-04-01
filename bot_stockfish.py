import mss
import cv2
import numpy as np
import chess
import chess.engine
import os
import time
import pyautogui

# --- CONFIGURATION DOSSIERS ---
DOSSIER_PROJET = r"C:\Users\giann\OneDrive\Bureau\IA chess\v2"
DOSSIER_TEMPLATES = os.path.join(DOSSIER_PROJET, "templates")

# TON CHEMIN STOCKFISH
EXE_STOCKFISH = os.path.join(DOSSIER_PROJET, r"stockfish\stockfish\stockfish-windows-x86-64-avx2.exe")

os.chdir(DOSSIER_PROJET)

# --- TES COORDONNÉES FIXES ---
# ⚠️ Si le bot voit du vide (8/8/8/8...), c'est que l'échiquier n'est plus EXACTEMENT ici :
ZONE_ECHIQUIER = {"top": 152, "left": 2317, "width": 803, "height": 807}
TRADUCTION_FEN = {'bB':'b','bK':'k','bN':'n','bP':'p','bQ':'q','bR':'r','wB':'B','wK':'K','wN':'N','wP':'P','wQ':'Q','wR':'R'}

TAILLE_X = ZONE_ECHIQUIER["width"] / 8
TAILLE_Y = ZONE_ECHIQUIER["height"] / 8
ORIGINE_X = ZONE_ECHIQUIER["left"] + (TAILLE_X / 2)
ORIGINE_Y = ZONE_ECHIQUIER["top"] + (TAILLE_Y / 2)

pyautogui.PAUSE = 0.05 

def charger_templates_masques():
    templates = {}
    for nom in TRADUCTION_FEN.keys():
        chemin = os.path.join(DOSSIER_TEMPLATES, f"{nom}.png")
        if not os.path.exists(chemin):
            print(f"❌ ERREUR: Silhouette manquante -> {nom}.png")
            exit()
        templates[nom] = cv2.imread(chemin, cv2.IMREAD_GRAYSCALE)
    return templates

def click_case(nom_case):
    col = ord(nom_case[0]) - ord('a')
    lig = 8 - int(nom_case[1])
    target_x = int(ORIGINE_X + (col * TAILLE_X))
    target_y = int(ORIGINE_Y + (lig * TAILLE_Y))
    pyautogui.moveTo(target_x, target_y, duration=0.1)
    pyautogui.click()

def calculer_droits_roque(plateau):
    droits = ""
    if plateau[60] == 'K':
        if plateau[63] == 'R': droits += "K"
        if plateau[56] == 'R': droits += "Q"
    if plateau[4] == 'k':
        if plateau[7] == 'r': droits += "k"
        if plateau[0] == 'r': droits += "q"
    return droits if droits != "" else "-"

def lire_fen_masque(templates):
    with mss.mss() as sct:
        img = np.array(sct.grab(ZONE_ECHIQUIER))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    masque = cv2.inRange(img_bgr, (0, 0, 0), (85, 85, 85))
    
    h, w = masque.shape
    th, tl = h / 8, w / 8
    plateau = []
    PAD = 12

    for y in range(8):
        for x in range(8):
            y1, y2 = int(y * th), int((y + 1) * th)
            x1, x2 = int(x * tl), int((x + 1) * tl)
            
            y_start = max(0, y1 - PAD)
            y_end = min(h, y2 + PAD)
            x_start = max(0, x1 - PAD)
            x_end = min(w, x2 + PAD)
            
            case_masque = masque[y_start:y_end, x_start:x_end]
            
            meilleur_score = 0
            meilleure_piece = '1'
            
            for nom, tmpl in templates.items():
                res = cv2.matchTemplate(case_masque, tmpl, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(res)
                if max_val > meilleur_score:
                    meilleur_score = max_val
                    meilleure_piece = nom
            
            if meilleur_score > 0.25:
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
        
    droits_roque = calculer_droits_roque(plateau)
    return fen, droits_roque

def main():
    print("👁️  Chargement des filtres optiques (Tampon Encreur)...")
    templates = charger_templates_masques()
    
    print("🧠 Connexion à Stockfish...")
    try:
        engine = chess.engine.SimpleEngine.popen_uci(EXE_STOCKFISH)
        engine.configure({"Threads": 4, "Hash": 1024}) 
    except FileNotFoundError:
        print(f"❌ ERREUR : Stockfish introuvable à : {EXE_STOCKFISH}")
        return

    couleur = input("Tu joues les Blancs (w) ou les Noirs (b) ? : ").lower()
    dernier_fen_brut = ""
    erreurs_vision = 0 
    
    print(f"🤖 BOT ARMÉ. Prêt à détruire. Couleur : {'Blancs' if couleur == 'w' else 'Noirs'}")

    try:
        while True:
            fen_brut, droits = lire_fen_masque(templates)
            
            if fen_brut != dernier_fen_brut:
                time.sleep(0.5) 
                fen_brut, droits = lire_fen_masque(templates)
                
                fen_complet = f"{fen_brut} {couleur} {droits} - 0 1"
                
                # --- LE DIAGNOSTIC EST LÀ ---
                print(f"👀 DEBUG VISION : {fen_brut}")
                
                try:
                    board = chess.Board(fen_complet)
                    erreurs_vision = 0 
                    
                    if not board.is_game_over():
                        print(f"🎯 FEN validé : {fen_brut}")
                        
                        result = engine.play(board, chess.engine.Limit(time=0.5))
                        move = result.move
                        
                        dep = chess.square_name(move.from_square)
                        arr = chess.square_name(move.to_square)
                        
                        print(f"🚀 Frappe : {dep} -> {arr}")
                        click_case(dep)
                        click_case(arr)
                        
                        time.sleep(0.5)
                        dernier_fen_brut, _ = lire_fen_masque(templates)
                    else:
                        print("🏁 Fin de partie détectée (Mat, Pat ou manque de matériel).")
                        break
                        
                except ValueError:
                    erreurs_vision += 1
                    if erreurs_vision >= 3:
                        print("\n🏆 L'échiquier est masqué (Pop-up de victoire ou de fin). Coupure du moteur.")
                        break
            
            time.sleep(0.2)
            
    except KeyboardInterrupt:
        print("\nArrêt manuel.")
    finally:
        engine.quit()

if __name__ == "__main__":
    main()