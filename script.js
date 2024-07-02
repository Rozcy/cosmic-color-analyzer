// Constants
const CHUNK_SIZE = 1024 * 1024; // 1 MB

// DOM Elements
const fileInput = document.getElementById('fileInput');
const imagePreview = document.getElementById('imagePreview');
const uploadButton = document.getElementById('uploadButton');
const analyzeButton = document.getElementById('analyzeButton');
const progressBar = document.getElementById('progressBar');
const resultsDiv = document.getElementById('results');

// Event Listeners
fileInput.addEventListener('change', handleFileSelection);
uploadButton.addEventListener('click', uploadFile);
analyzeButton.addEventListener('click', analyzeColors);

// File Handling Functions
function handleFileSelection(event) {
    const file = event.target.files[0];
    if (file) {
        console.log('File selected:', file.name, 'Size:', file.size, 'bytes');
        displayImagePreview(file);
    } else {
        console.log('No file selected');
    }
}

function displayImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        imagePreview.src = e.target.result;
        imagePreview.style.display = 'block';
        uploadButton.style.display = 'block';
        analyzeButton.disabled = true;
        console.log('Image preview loaded');
    };
    reader.onerror = function(e) {
        console.error('Error reading file:', e);
    };
    reader.readAsDataURL(file);
}

// Upload Functions
async function uploadFile() {
    console.log('Upload initiated');
    await uploadFileInChunks();
}

async function uploadFileInChunks() {
    const file = fileInput.files[0];
    if (!file) {
        console.error('No file selected');
        alert('Please select an image file.');
        return;
    }

    console.log('File to upload:', file.name, 'Size:', file.size, 'bytes');

    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
    const fileChecksum = await calculateChecksum(file);

    console.log('Total chunks:', totalChunks, 'Checksum:', fileChecksum);

    // Iterate through file chunks and upload them individually
    for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
        const chunk = file.slice(chunkIndex * CHUNK_SIZE, (chunkIndex + 1) * CHUNK_SIZE);
        const formData = createFormData(file, chunk, chunkIndex, totalChunks, fileChecksum);

        try {
            const response = await uploadChunk(formData);
            console.log('Chunk upload response:', response);
            updateProgressBar(chunkIndex + 1, totalChunks);
        } catch (error) {
            console.error('Error uploading chunk:', error);
            alert('Error uploading file chunk. Please try again.');
            return;
        }
    }

    console.log('Upload completed successfully!');
    alert('Upload successful!');
    analyzeButton.disabled = false;
}

function createFormData(file, chunk, chunkIndex, totalChunks, fileChecksum) {
    const formData = new FormData();
    formData.append('file', chunk, file.name);
    formData.append('chunk', chunkIndex.toString());
    formData.append('totalChunks', totalChunks.toString());
    formData.append('fileChecksum', fileChecksum);
    return formData;
}

async function uploadChunk(formData) {
    console.log('Uploading chunk...');
    logFormData(formData);

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
            headers: {
                'Content-Length': formData.get('file').size.toString()
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
        }

        return await response.text();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

function updateProgressBar(uploadedChunks, totalChunks) {
    const percentComplete = (uploadedChunks / totalChunks) * 100;
    progressBar.style.width = percentComplete + '%';
}

// Utility Functions
function logFormData(formData) {
    for (let [key, value] of formData.entries()) {
        if (key === 'file') {
            console.log(key, 'File blob, size:', value.size);
        } else {
            console.log(key, value);
        }
    }
}

// Checksum calculation function
async function calculateChecksum(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const arrayBuffer = e.target.result;
            const wordArray = CryptoJS.lib.WordArray.create(arrayBuffer);
            const checksum = CryptoJS.MD5(wordArray).toString();
            resolve(checksum);
        };
        reader.onerror = function(e) {
            reject(e);
        };
        reader.readAsArrayBuffer(file);
    });
}

// Color Analysis Function
function analyzeColors() {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', '/analyze', true);
    
    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                hideWaitingIndicator();
                displayResults(JSON.parse(xhr.responseText));
            } else {
                hideWaitingIndicator();
                console.error('Error analyzing image:', xhr.status, xhr.statusText);
                console.error('Response:', xhr.responseText);
                alert(`Error analyzing image: ${xhr.responseText}`);
            }
        }
    };

    xhr.onerror = function() {
        hideWaitingIndicator();
        console.error('Network error occurred');
        alert('A network error occurred. Please check your connection and try again.');
    };

    showWaitingIndicator();
    xhr.send();
}

// Waiting Indicator Functions
function showWaitingIndicator() {
    resultsDiv.innerHTML = '<div class="waiting-indicator">Analyzing colors... <div class="spinner"></div></div>';
}

function hideWaitingIndicator() {
    resultsDiv.innerHTML = '';
}

// Result Display Function
function displayResults(data) {
    resultsDiv.innerHTML = '<h2>Top 5 Cosmic Colors:</h2>';
    data.colors.forEach(function(color) {
        const colorBar = document.createElement('div');
        colorBar.className = 'color-bar';
        colorBar.innerHTML = `
            <div class="color-sample" style="background-color: rgb(${color.r},${color.g},${color.b});"></div>
            <span>R: ${color.r}, G: ${color.g}, B: ${color.b} - ${color.percentage}</span>
        `;
        resultsDiv.appendChild(colorBar);
    });
}