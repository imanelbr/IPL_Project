import cv2
import mediapipe as mp
import numpy as np
import time

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialiser le détecteur de main
hands = mp_hands.Hands()

def detect_gestures(hand_landmarks):

    # Vérifier le signe de la paix/victoire
    peace_sign = (hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
                  hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
                  hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y > hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y and
                  hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y > hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y)

    if peace_sign:
        return "Yo, whats'up"



# Configuration de la webcam
cap = cv2.VideoCapture(0)

# Variables pour le suivi du mouvement
history_x = []
motion_threshold = 30  # Seuil de détection de mouvement

# Compteur de basculement
flip_count = 0

# Variables pour le jeu Chifoumi
player_score = 0
computer_score = 0
rounds_played = 0
winning_score = 3
game_in_progress = True  # Ajoutez cette variable pour suivre l'état du jeu

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    # Détecter les mains dans l'image
    results = hands.process(frame)
    gesture = "None"
    if results.multi_hand_landmarks:
        for landmarks in results.multi_hand_landmarks:
            # Dessiner les landmarks de la main sur l'image
            mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)
            gesture = detect_gestures(landmarks)
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
            cv2.putText(frame, f"Fingers: {finger_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Suivi du mouvement de la main
            hand_center_x = int(np.mean([landmarks.landmark[i].x * frame.shape[1] for i in range(21)]))
            history_x.append(hand_center_x)

            if len(history_x) > 3:
                # Vérifier si la main bascule de gauche à droite trois fois
                if history_x[-1] < frame.shape[1] // 2 - motion_threshold and history_x[-2] > frame.shape[1] // 2 + motion_threshold:
                    flip_count += 1
                    history_x.clear()

            # Afficher le nombre de basculements
            #cv2.putText(frame, f"flip: {flip_count}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Si trois basculements sont détectés, afficher "hello"
            if flip_count >= 2:
                cv2.putText(frame, "Hello !", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.putText(frame, gesture, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
    # Afficher l'image avec les résultats
    cv2.imshow('Hand Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()
