// Load face-api models from static folder or CDN
// Load face-api.js model
Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('/static/Evoting/models')
]).then(startWebcam).catch(err => {
    console.error("Model loading failed:", err);
    alert("Failed to load face detection model.");
});

const video = document.getElementById('video');  // match your HTML
const canvas = document.getElementById('canvas'); // match your HTML
const captureButton = document.getElementById('capture');
const retakeButton = document.getElementById('retake');
const imageInput = document.getElementById('photoData'); // match your HTML
const previewImage = document.getElementById('preview');

function startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
        .then(stream => {
            video.srcObject = stream;
            captureButton.disabled = false;  // enable capture once ready
        })
        .catch(err => {
            alert("Please allow webcam access to capture your photo.");
            console.error("Webcam error:", err);
        });
}
