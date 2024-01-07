import cv2
import mediapipe as mp
import numpy as np
import random
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialiser le détecteur de main
hands = mp_hands.Hands()

# Configuration de la webcam
cap = cv2.VideoCapture(0)

# Variables pour le jeu Chifoumi
player_score = 0
computer_score = 0
rounds_played = 0
winning_score = 3
game_in_progress = False  # Ajoutez cette variable pour suivre l'état du jeu
round_start_time = 0
game_over = False
def display_countdown(cap, countdown_time):
    for i in range(countdown_time, 0, -1):
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.putText(frame, str(i), (frame.shape[1]//2, frame.shape[0]//2), cv2.FONT_HERSHEY_SIMPLEX, 5, (255, 0, 0), 10)
        cv2.imshow('Hand Tracking', frame)
        cv2.waitKey(1000)  # Attendre 1 seconde

# Délai initial de 5 secondes avant le début du jeu

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    # Détecter les mains dans l'image
    results = hands.process(frame)
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Dessiner les landmarks de la main sur l'image
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
            # Compter le nombre de doigts levés
            finger_count = 0
            if results.multi_handedness[0].classification[0].label == 'Right':
                # Si c'est la main gauche, vérifiez la position en X du bout du pouce par rapport au joint entre le pouce et l'index
                if landmarks.landmark[4].y < landmarks.landmark[3].y and landmarks.landmark[4].x < landmarks.landmark[3].x:
                    finger_count += 1
            else:
                # Si c'est la main droite, vérifiez la position en X du bout du pouce par rapport au joint entre le pouce et l'index
                if landmarks.landmark[4].y < landmarks.landmark[3].y and landmarks.landmark[4].x > landmarks.landmark[3].x:
                    finger_count += 1
            if landmarks.landmark[8].y < landmarks.landmark[7].y:
                finger_count += 1
            if landmarks.landmark[12].y < landmarks.landmark[11].y:
                finger_count += 1
            if landmarks.landmark[16].y < landmarks.landmark[15].y:
                finger_count += 1
            if landmarks.landmark[20].y < landmarks.landmark[19].y:
                finger_count += 1

            # Afficher le nombre de doigts levés
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            time.sleep(2)
            if not game_in_progress:
            # Afficher le compte à rebours avant chaque manche
                display_countdown(cap, 2)  # Compte à rebours de 2 secondes
                round_start_time = time.time()  # Enregistrer le temps de début de la manche
                game_in_progress = True

            # Calculer le temps écoulé depuis le début de la manche
            elapsed_time = time.time() - round_start_time

            if elapsed_time < 2:  # Afficher le résultat de la manche pendant 2 secondes
                if game_in_progress:
                    # Logique du jeu Chifoumi
                    if finger_count == 2:  # Index et majeur levés
                        player_choice = "ciseaux"
                    elif finger_count == 5:  # Tous les doigts levés
                        player_choice = "feuille"
                    elif finger_count == 0:  # Tous les doigts levés
                        player_choice = "pierre"
                    else:
                        player_choice = "invalid"  # ou gérez les gestes invalides d'une autre manière

                    computer_choice = random.choice(["pierre", "feuille", "ciseaux"])

                    # Déterminer le vainqueur de la manche
                    if player_choice == computer_choice:
                        result = "Egalite"
                    elif (
                        (player_choice == "pierre" and computer_choice == "ciseaux")
                        or (player_choice == "ciseaux" and computer_choice == "feuille")
                        or (player_choice == "feuille" and computer_choice == "pierre")
                    ):
                        player_score += 1
                        result = "Joueur gagne"
                    else:
                        computer_score += 1
                        result = "Ordinateur gagne"

                    rounds_played += 1

                # Afficher le résultat de la manche
                cv2.putText(frame, f"Joueur: {player_choice}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(frame, f"Ordinateur: {computer_choice}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(frame, f"Resultat: {result}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.putText(frame, f"Score: Joueur {player_score} - {computer_score} Ordinateur", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

                # Vérifier si l'un des joueurs a atteint le score gagnant
                if player_score == winning_score or computer_score == winning_score:
                    winner = "Joueur" if player_score == winning_score else "Ordinateur"
                    game_over = True
                    cv2.putText(frame, f"{winner} remporte la partie!", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                    game_in_progress = False  # Le jeu est terminé, désactivez la logique du jeu
                if game_over:
                    continue   
            else:
                # Réinitialisez le jeu pour la prochaine manche
                game_in_progress = False
                # (Ajoutez ici la réinitialisation des variables de la manche, comme player_choice, computer_choice, etc.)

    # Afficher l'image avec les résultats
    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()
