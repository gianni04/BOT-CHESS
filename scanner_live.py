import cv2
import numpy as np
import mss
import pickle

monitor = {'top': 148, 'left': 2185, 'width': 816, 'height': 816}

with open("memoire_bot.pkl", 'rb') as f:
    memoire = pickle.load(f)

def dhash(image, hash_size=16):
    resized = cv2.resize(image, (hash_size + 1, hash_size))
    diff = resized[:, 1:] > resized[:, :-1]
    return diff.flatten()

def lire_plateau():
    with mss.mss() as sct:
        capture = cv2.cvtColor(np.array(sct.grab(monitor)), cv2.COLOR_BGR2GRAY)
        taille_case = 816 // 8
        fen_rows = []
        for i_lig in range(8):
            vides, row_str = 0, ""
            for i_col in range(8):
                y, x = i_lig * taille_case, i_col * taille_case
                h_actuel = dhash(capture[y:y+taille_case, x:x+taille_case])
                
                meilleure_piece, min_diff = "?", 10000
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

if __name__ == "__main__":
    print(f"Position détectée : {lire_plateau()}")