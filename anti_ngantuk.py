import cv2
import mediapipe as mp
import math
import pyttsx3
import threading

# Fungsi untuk bersuara tanpa membuat video macet (menggunakan thread)
def speak():
    engine = pyttsx3.init()
    engine.setProperty('rate', 160) # Kecepatan bicara
    engine.say("Woi bangun! Jangan tidur, ayo belajar lagi!")
    engine.runAndWait()

def play_alarm():
    t = threading.Thread(target=speak)
    t.start()

# Fungsi menghitung jarak antara dua titik
def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

# Fungsi menghitung bukaan mata (Eye Aspect Ratio)
def get_ear(eye_points, facial_landmarks):
    p = [facial_landmarks.landmark[i] for i in eye_points]
    
    v1 = distance(p[1], p[5])
    v2 = distance(p[2], p[4])
    h = distance(p[0], p[3])
    
    return (v1 + v2) / (2.0 * h) if h != 0 else 0

# Inisialisasi Deteksi Wajah
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Indeks titik mata (berdasarkan standar Mediapipe)
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

cap = cv2.VideoCapture(0) # 0 adalah kamera bawaan laptop
sleep_frames = 0

print("Kamera menyala! Tekan tombol 'q' pada keyboard untuk keluar.")

while True:
    ret, frame = cap.read()
    if not ret: break
        
    # Balik gambar seperti cermin
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            left_ear = get_ear(LEFT_EYE, face_landmarks)
            right_ear = get_ear(RIGHT_EYE, face_landmarks)
            ear = (left_ear + right_ear) / 2.0

            # Jika rasio mata mengecil (tertutup)
            if ear < 0.25: 
                sleep_frames += 1
                # Jika tertutup lebih dari ~15 frame (sekitar 1-2 detik)
                if sleep_frames > 15: 
                    cv2.putText(frame, "WOI BANGUN!!!", (50, 100), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
                    
                    if sleep_frames == 16: # Panggil alarm sekali saja
                        play_alarm()
            else:
                sleep_frames = 0 # Reset hitungan jika mata melek
                cv2.putText(frame, "Lanjut Belajar...", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Detektor Ngantuk (Python)", frame)

    # Tekan 'q' untuk menutup program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()