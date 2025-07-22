// Load FaceAPI model
Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('/static/Evoting/models')
])
.then(startWebcam)
.catch(err => {
    console.error("Model loading failed:", err);
    alert("Failed to load face detection model.");
});

// DOM elements
const videoEl = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture');
const retakeBtn = document.getElementById('retake');
const imageInput = document.getElementById('photoData');
const previewImage = document.getElementById('preview');
const faceStatus = document.getElementById('faceStatus');
const previewSection = document.getElementById('previewSection');


let captured = false;
let faceDetected = false;

// Start webcam
function startWebcam() {
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
        .then(stream => {
            videoEl.srcObject = stream;
            captureBtn.disabled = false;
        })
        .catch(err => {
            alert("Please allow webcam access to capture your photo.");
            console.error("Webcam error:", err);
        });
}

// Capture photo and detect face
async function capturePhoto() {
    const context = canvas.getContext("2d");
    context.drawImage(videoEl, 0, 0, canvas.width, canvas.height);

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
        retakeBtn.style.display = "inline-block"; // Show the button
        previewSection.style.display = "block";      // Show the preview area
        previewImage.src = "{% static 'Evoting/images/default-profile.png' %}"; // Reset preview
        faceStatus.style.color = "red";
    }

    captureBtn.style.display = "none";
    retakeBtn.style.display = "inline-block";
    videoEl.style.display = "none";
}

// Retake photo
function retakePhoto() {
    captured = false;
    faceDetected = false;
    imageInput.value = '';
    previewImage.src = '';
    previewImage.style.display = "none";
    faceStatus.textContent = '';

    captureBtn.style.display = "inline-block";
    retakeBtn.style.display = "none";
    videoEl.style.display = "block";
}

// Validate form before submitting
function validateAndSubmit(event) {
    if (!captured) {
        event.preventDefault();
        alert("Please capture a photo first.");
    } else if (!faceDetected) {
        event.preventDefault();
        alert("No face detected. Please retake the photo.");
        return false;
    }
    return true; // Allow form submission if validation passes
}

// Initialize on DOM load
document.addEventListener("DOMContentLoaded", () => {
    captureBtn.addEventListener("click", capturePhoto);
    retakeBtn.addEventListener("click", retakePhoto);

    const form = document.querySelector("#VoterRegistrationForm");
    if (form) {
        form.addEventListener("submit", validateAndSubmit);
    } else {
        console.warn("Form with ID 'VoterRegistrationForm' not found.");
    }
});
