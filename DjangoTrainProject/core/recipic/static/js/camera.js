document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureButton = document.getElementById('capture');
    const loadingElement = document.getElementById('loading');
    const resultElement = document.getElementById('result');
    const foodNameElement = document.getElementById('foodName');
    const confidenceElement = document.getElementById('confidence');
    const context = canvas.getContext('2d');

    // Check model status
    fetch('/api/model-status/')
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'success') {
                alert(`Model not loaded properly: ${data.message}`);
                captureButton.disabled = true;
            }
        })
        .catch(error => {
            console.error('Error checking model status:', error);
            alert('Error checking model status. Please refresh the page.');
            captureButton.disabled = true;
        });

    // Request camera access
    navigator.mediaDevices.getUserMedia({ 
        video: { 
            facingMode: 'environment',
            width: { ideal: 640 },
            height: { ideal: 480 }
        } 
    })
    .then(function(stream) {
        video.srcObject = stream;
    })
    .catch(function(err) {
        console.error("Camera error:", err);
        alert("Error accessing camera. Please make sure you've granted camera permissions.");
    });

    // Handle image capture and classification
    captureButton.addEventListener('click', async function() {
        // Show loading state
        loadingElement.style.display = 'flex';
        resultElement.style.display = 'none';

        // Capture frame from video
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        try {
            // Convert canvas to blob
            const blob = await new Promise(resolve => {
                canvas.toBlob(resolve, 'image/jpeg', 0.95);
            });

            // Create form data
            const formData = new FormData();
            formData.append('image', blob, 'food.jpg');

            // Send to backend
            const response = await fetch('/api/classify/', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Server error: ${errorData.error}`);
            }

            const data = await response.json();

            // Update results
            foodNameElement.textContent = data.class_name;
            confidenceElement.textContent = `Confidence: ${(data.confidence * 100).toFixed(2)}%`;
            
            // Hide loading, show results
            loadingElement.style.display = 'none';
            resultElement.style.display = 'block';
        } catch (error) {
            console.error('Error:', error);
            alert(`Error classifying image: ${error.message}`);
            loadingElement.style.display = 'none';
            resultElement.style.display = 'block';
            foodNameElement.textContent = 'Error occurred';
            confidenceElement.textContent = 'Please try again';
        }
    });
});