const video = document.getElementById('video');
const alertSound = document.getElementById('alertSound');
const startButton = document.getElementById('startButton');
let isPlaying = false; 

// Menunggu tombol diklik sebelum memuat AI dan kamera
startButton.addEventListener('click', () => {
    Promise.all([
        faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
        faceapi.nets.faceLandmark68Net.loadFromUri('/models')
    ]).then(startVideo);
    
    startButton.style.display = 'none'; // Sembunyikan tombol setelah mulai
});

function startVideo() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream)
        .catch(err => console.error("Gagal akses webcam:", err));
}

video.addEventListener('play', () => {
    setInterval(async () => {
        const detections = await faceapi.detectAllFaces(video, new faceapi.TinyFaceDetectorOptions()).withFaceLandmarks();

        if (detections.length > 0) {
            const landmarks = detections[0].landmarks;
            const leftEye = landmarks.getLeftEye();
            const rightEye = landmarks.getRightEye();

            const leftEAR = calculateEAR(leftEye);
            const rightEAR = calculateEAR(rightEye);
            const avgEAR = (leftEAR + rightEAR) / 2;

            // Jika nilai EAR di bawah 0.25, mata dianggap terpejam
            if (avgEAR < 0.25) {
                if (!isPlaying) {
                    alertSound.play();
                    isPlaying = true;
                    
                    alertSound.onended = () => {
                        isPlaying = false;
                    };
                }
            }
        }
    }, 500); 
});

function calculateEAR(eye) {
    const vert1 = Math.hypot(eye[1].x - eye[5].x, eye[1].y - eye[5].y);
    const vert2 = Math.hypot(eye[2].x - eye[4].x, eye[2].y - eye[4].y);
    const horiz = Math.hypot(eye[0].x - eye[3].x, eye[0].y - eye[3].y);
    return (vert1 + vert2) / (2.0 * horiz);
}