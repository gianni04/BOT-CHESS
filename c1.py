import pyautogui
import time

print("1️⃣ Place ta souris pile sur le coin TOUT EN HAUT À GAUCHE de l'échiquier (bordure de la case a8/h8) et ne bouge plus...")
time.sleep(4)
x1, y1 = pyautogui.position()
print(f"✅ Haut-Gauche capturé : {x1}, {y1}")

print("\n2️⃣ Place ta souris pile sur le coin TOUT EN BAS À DROITE de l'échiquier (bordure de la case h1/a1) et ne bouge plus...")
time.sleep(4)
x2, y2 = pyautogui.position()
print(f"✅ Bas-Droite capturé : {x2}, {y2}")

largeur = x2 - x1
hauteur = y2 - y1

print("\n=========================================")
print("🎯 COPIE-COLLE CETTE LIGNE :")
print(f'ZONE_ECHIQUIER = {{"top": {y1}, "left": {x1}, "width": {largeur}, "height": {hauteur}}}')
print("=========================================")