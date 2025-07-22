// Load face detection model
Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('/static/Evoting/models')
]).then(startWebcam).catch(err => {
    console.error("Model loading failed:", err);
    alert("Failed to load face detection model.");
});

const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureButton = document.getElementById('capture');
const retakeButton = document.getElementById('retake');
const imageInput = document.getElementById('photoData');
const previewImage = document.getElementById('preview');
const faceStatus = document.getElementById('faceStatus');

let captured = false;
let faceDetected = false;

function startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
        .then(stream => {
            video.srcObject = stream;
            captureButton.disabled = false;
        })
        .catch(err => {
            alert("Please allow webcam access.");
            console.error("Webcam error:", err);
        });
}

async function capturePhoto() {
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    const base64Image = canvas.toDataURL("image/jpeg");
    previewImage.src = base64Image;
    previewImage.style.display = "block";
    imageInput.value = base64Image;
    captured = true;

    const detection = await faceapi.detectSingleFace(canvas, new faceapi.TinyFaceDetectorOptions());

    if (detection) {
        faceDetected = true;
        faceStatus.textContent = "Face detected. You may proceed.";
        faceStatus.style.color = "green";
    } else {
        faceDetected = false;
        faceStatus.textContent = "No face detected. Please retake the photo.";
        faceStatus.style.color = "red";
    }

    captureButton.style.display = "none";
    retakeButton.style.display = "inline-block";
    video.style.display = "none";
}

function retakePhoto() {
    captured = false;
    faceDetected = false;
    imageInput.value = '';
    previewImage.src = '';
    previewImage.style.display = "none";
    faceStatus.textContent = '';

    captureButton.style.display = "inline-block";
    retakeButton.style.display = "none";
    video.style.display = "block";
}

function validateAndSubmit(event) {
    if (!captured) {
        event.preventDefault();
        alert("Please capture a photo first.");
    } else if (!faceDetected) {
        event.preventDefault();
        alert("No face detected. Please retake the photo.");
    }
}

// Hook everything after DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    captureButton.addEventListener("click", capturePhoto);
    retakeButton.addEventListener("click", retakePhoto);
    document.querySelector("#VoterRegistrationForm").addEventListener("submit", validateAndSubmit);
});
