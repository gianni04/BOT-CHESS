import cv2
import numpy as np
import os
import pickle

fichier_memoire = "memoire_bot.pkl"
# Position de départ standard pour l'apprentissage
position_depart = [
    ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
    ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.', '.'],
    ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
    ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
]

def dhash(image, hash_size=16):
    resized = cv2.resize(image, (hash_size + 1, hash_size))
    diff = resized[:, 1:] > resized[:, :-1]
    return diff.flatten()

def apprendre():
    memoire = {}
    colonnes, lignes = 'abcdefgh', '87654321'
    print("Mise à jour de la mémoire (Format 16x16)...")
    for i_lig in range(8):
        for i_col in range(8):
            img = cv2.imread(f"cases/{colonnes[i_col]}{lignes[i_lig]}.png", 0)
            if img is None: continue
            h = dhash(img)
            piece = position_depart[i_lig][i_col]
            if piece not in memoire: memoire[piece] = []
            memoire[piece].append(h)
    with open(fichier_memoire, 'wb') as f:
        pickle.dump(memoire, f)
    print("Mémoire prête !")

if __name__ == "__main__": apprendre()