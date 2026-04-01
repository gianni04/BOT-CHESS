import cv2
import numpy as np
import mss
import pickle
import chess
import chess.engine
import pyautogui
import time
import os

# Coordonnées corrigées
monitor = {'top': 148, 'left': 2192, 'width': 808, 'height': 808}
# Chemin universel pour Stockfish
STOCKFISH_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stockfish.exe")

with open("memoire_bot.pkl", 'rb') as f:
    memoire = pickle.load(f)

def dhash(image, hash_size=16):
    resized = cv2.resize(image, (hash_size + 1, hash_size))
    diff = resized[:, 1:] > resized[:, :-1]
    return diff.flatten()

def obtenir_fen_actuel():
    with mss.mss() as sct:
        capture = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGR2GRAY)
        taille_case = 808 // 8
        fen_rows = []
        for i_lig in range(8):
            vides, row_str = 0, ""
            for i_col in range(8):
                y, x = i_lig * taille_case, i_col * taille_case
                h_actuel = dhash(capture[y:y+taille_case, x:x+taille_case])
                meilleure_piece, min_diff = ".", 10000
                for piece, signatures in memoire.items():
                    for s in signatures:
                        diff = np.count_nonzero(h_actuel != s)
                        if diff < min_diff:
                            min_diff, meilleure_piece = diff, piece
                if meilleure_piece == '.': vides += 1
                else:
                    if vides > 0: row_str += str(vides); vides = 0
                    row_str += meilleure_piece
            if vides > 0: row_str += str(vides)
            fen_rows.append(row_str)
        return "/".join(fen_rows)

def jouer_coup(coup_uci):
    cols, lins = "abcdefgh", "87654321"
    def clic(c):
        x = monitor["left"] + (cols.index(c[0]) * 101) + 50
        y = monitor["top"] + (lins.index(c[1]) * 101) + 50
        pyautogui.click(x, y)
        time.sleep(0.05)
    clic(coup_uci[:2])
    clic(coup_uci[2:4])

def main():
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    except Exception as e:
        print(f"ERREUR : Stockfish introuvable à l'adresse {STOCKFISH_PATH}")
        return

    print("=== BOT EN LIGNE ET PRÊT À ÉCRASER ===")
    derniere_fen = ""
    
    try:
        while True:
            fen = obtenir_fen_actuel()
            if fen != derniere_fen:
                # On vérifie si la position est valide (présence des rois notamment)
                try:
                    board = chess.Board(fen + " w - - 0 1")
                    if "K" in fen and "k" in fen: # Sécurité : les deux rois doivent être vus
                        print(f"Position lue : {fen}")
                        res = engine.play(board, chess.engine.Limit(time=0.4))
                        print(f"Coup calculé : {res.move}")
                        jouer_coup(str(res.move))
                        derniere_fen = obtenir_fen_actuel()
                    else:
                        print("Attente d'une position claire (Rois non détectés)...")
                except:
                    pass
            time.sleep(0.8)
    except KeyboardInterrupt:
        engine.quit()

if __name__ == "__main__":
    main()