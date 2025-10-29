// Global variables
let currentTab = 'hide';

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function () {
    initializeApp();
    setupEventListeners();
    checkSystemHealth();
});

function initializeApp() {
    console.log('🚀 Initializing Python Blockchain Steganography App');

    // Check if we're running on the correct port
    if (window.location.port !== '5000' && window.location.hostname === 'localhost') {
        console.warn('⚠️ App should be running on port 5000');
    }
}

function setupEventListeners() {
    // Image file change listener
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', handleImageSelection);
    }

    // Secret data character counter
    const secretDataTextarea = document.getElementById('secretData');
    if (secretDataTextarea) {
        secretDataTextarea.addEventListener('input', updateCharCount);
    }

    // Form submit listeners
    const hideForm = document.getElementById('hideForm');
    if (hideForm) {
        hideForm.addEventListener('submit', handleHideData);
    }

    const extractForm = document.getElementById('extractForm');
    if (extractForm) {
        extractForm.addEventListener('submit', handleExtractData);
    }

    const verifyForm = document.getElementById('verifyForm');
    if (verifyForm) {
        verifyForm.addEventListener('submit', handleVerifyOwnership);
    }
}

function switchTab(tabName, event) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });

    // Show selected tab content
    document.getElementById(tabName).classList.add('active');

    // Add active class to clicked tab button
    if (event) event.target.classList.add('active');

    currentTab = tabName;

    // Load tab-specific data
    if (tabName === 'analytics') {
        checkSystemHealth();
    }
}

async function checkSystemHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();

        // Update status indicators
        updateStatusIndicator('ipfs-status', data.ipfs === 'connected');
        updateStatusIndicator('blockchain-status', data.blockchain === 'connected');

        // Update analytics if on analytics tab
        if (currentTab === 'analytics') {
            updateSystemHealthDisplay(data);
        }

    } catch (error) {
        console.error('Health check failed:', error);
        updateStatusIndicator('ipfs-status', false);
        updateStatusIndicator('blockchain-status', false);
    }
}

function updateStatusIndicator(elementId, isConnected) {
    const element = document.getElementById(elementId);
    if (!element) return;

    element.classList.remove('connected', 'disconnected', 'checking');

    if (isConnected) {
        element.classList.add('connected');
        element.textContent = elementId === 'ipfs-status'
            ? '✅ IPFS Connected'
            : '✅ Blockchain Connected';
    } else {
        element.classList.add('disconnected');
        element.textContent = elementId === 'ipfs-status'
            ? '❌ IPFS Disconnected'
            : '❌ Blockchain Disconnected';
    }
}

function updateSystemHealthDisplay(healthData) {
    const systemHealthDiv = document.getElementById('systemHealth');
    if (!systemHealthDiv) return;

    systemHealthDiv.innerHTML = `
        <div class="analytics-grid">
            <div class="analytics-item">
                <div class="number">${healthData.ipfs === 'connected' ? '✅' : '❌'}</div>
                <div class="label">IPFS Status</div>
            </div>
            <div class="analytics-item">
                <div class="number">${healthData.blockchain === 'connected' ? '✅' : '❌'}</div>
                <div class="label">Blockchain Status</div>
            </div>
            <div class="analytics-item">
                <div class="number">${healthData.status}</div>
                <div class="label">Overall Health</div>
            </div>
            <div class="analytics-item">
                <div class="number">${new Date(healthData.timestamp).toLocaleTimeString()}</div>
                <div class="label">Last Check</div>
            </div>
        </div>
    `;
}

function handleImageSelection(event) {
    const file = event.target.files[0];
    const infoDiv = document.getElementById('imageInfo');

    if (!file) {
        infoDiv.innerHTML = '';
        return;
    }

    // Display file information
    const fileSize = formatFileSize(file.size);
    const fileType = file.type;

    infoDiv.innerHTML = `
        <strong>Selected:</strong> ${file.name}<br>
        <strong>Size:</strong> ${fileSize}<br>
        <strong>Type:</strong> ${fileType}
    `;

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/tiff'];
    if (!allowedTypes.includes(fileType.toLowerCase())) {
        infoDiv.innerHTML += '<br><span style="color: #dc3545;">⚠️ Warning: This file type may not be supported</span>';
    }

    // Check file size (16MB limit)
    if (file.size > 16 * 1024 * 1024) {
        infoDiv.innerHTML += '<br><span style="color: #dc3545;">⚠️ Warning: File too large (max 16MB)</span>';
    }
}

function updateCharCount() {
    const textarea = document.getElementById('secretData');
    const counter = document.getElementById('charCount');

    if (textarea && counter) {
        counter.textContent = textarea.value.length;

        // Color coding for length
        if (textarea.value.length > 1000) {
            counter.style.color = '#dc3545'; // Red
        } else if (textarea.value.length > 500) {
            counter.style.color = '#ffc107'; // Yellow
        } else {
            counter.style.color = '#666'; // Gray
        }
    }
}

async function handleHideData(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const button = event.target.querySelector('button[type="submit"]');
    const resultDiv = document.getElementById('hideResult');

    // Validate form
    const file = formData.get('image');
    const secretData = formData.get('secretData');

    if (!file || !secretData) {
        showResult(resultDiv, 'error', 'Please fill in all required fields');
        return;
    }

    // Show loading state
    button.disabled = true;
    button.textContent = '🔄 Processing...';
    showResult(resultDiv, 'info', 'Processing image and storing on blockchain...', true);

    try {
        const response = await fetch('/api/hide', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            showResult(resultDiv, 'success', `✅ Data hidden successfully!<br>
                <strong>Image ID:</strong> ${data.imageId}<br>
                <strong>IPFS Hash:</strong> ${data.ipfsHash}<br>
                <strong>Transaction Hash:</strong> ${data.transactionHash}<br>
                <strong>Block Number:</strong> ${data.blockNumber}<br><br>
                <button onclick="downloadSteganographicImage('${data.imageId}')" class="btn btn-success" style="margin-top: 10px;">
                    📥 Download Steganographic Image
                </button>`);
        } else {
            showResult(resultDiv, 'error', `❌ Failed: ${data.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Hide data error:', error);
        showResult(resultDiv, 'error', '❌ An error occurred while hiding data');
    } finally {
        button.disabled = false;
        button.textContent = 'Hide Data';
    }
}

async function handleExtractData(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const resultDiv = document.getElementById('extractResult');
    const button = event.target.querySelector('button[type="submit"]');

    // Get form values
    const imageId = formData.get('imageId');
    const password = formData.get('password');

    if (!imageId) {
        showResult(resultDiv, 'error', 'Please enter an Image ID');
        return;
    }

    // Show loading state
    button.disabled = true;
    button.textContent = '🔄 Extracting...';
    showResult(resultDiv, 'info', 'Retrieving data from blockchain and IPFS...', true);

    try {
        const response = await fetch('/api/extract', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                imageId: imageId,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Get image ID from the form
            const imageId = document.getElementById('imageId').value;
            showResult(resultDiv, 'success', `✅ Extracted Data:<br><strong>${data.data}</strong><br><br>
                <strong>Metadata:</strong><br>
                Owner: ${data.metadata.owner}<br>
                Timestamp: ${data.metadata.timestamp}<br>
                Original Filename: ${data.metadata.originalFilename}<br>
                File Size: ${data.metadata.fileSize} bytes<br><br>
                <button onclick="downloadSteganographicImage('${imageId}')" class="btn btn-success" style="margin-top: 10px;">
                    📥 Download Steganographic Image
                </button>`);
        } else {
            showResult(resultDiv, 'error', `❌ Failed: ${data.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Extract data error:', error);
        showResult(resultDiv, 'error', '❌ An error occurred while extracting data');
    } finally {
        button.disabled = false;
        button.textContent = '🔓 Extract Data from Blockchain';
    }
}

async function handleVerifyOwnership(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const resultDiv = document.getElementById('verifyResult');
    const button = event.target.querySelector('button[type="submit"]');

    // Get form values
    const imageId = formData.get('imageId');
    const userAddress = formData.get('userAddress');

    if (!imageId || !userAddress) {
        showResult(resultDiv, 'error', 'Please fill in all required fields');
        return;
    }

    // Show loading state
    button.disabled = true;
    button.textContent = '🔄 Verifying...';
    showResult(resultDiv, 'info', 'Checking ownership on blockchain...', true);

    try {
        const response = await fetch('/api/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                imageId: imageId,
                userAddress: userAddress
            })
        });

        const data = await response.json();

        if (response.ok) {
            if (data.isOwner) {
                // Get image ID from the form
                const imageId = document.getElementById('verifyImageId').value;
                showResult(resultDiv, 'success', `✅ Ownership Verified!<br><br>
                    <strong>Record Details:</strong><br>
                    Owner: ${data.record.owner}<br>
                    IPFS Hash: ${data.record.ipfsHash}<br>
                    Metadata Hash: ${data.record.metadataHash}<br>
                    Timestamp: ${data.record.timestamp}<br>
                    Exists: ${data.record.exists ? 'Yes' : 'No'}<br><br>
                    <button onclick="downloadSteganographicImage('${imageId}')" class="btn btn-success" style="margin-top: 10px;">
                        📥 Download Steganographic Image
                    </button>`);
            } else {
                showResult(resultDiv, 'error', `❌ Ownership Verification Failed:<br>You are not the owner of this image.`);
            }
        } else {
            showResult(resultDiv, 'error', `❌ Verification Failed: ${data.error || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Verify ownership error:', error);
        showResult(resultDiv, 'error', '❌ An error occurred while verifying ownership');
    } finally {
        button.disabled = false;
        button.textContent = '✅ Verify Ownership';
    }
}

// Utility: format file size
function formatFileSize(sizeBytes) {
    if (sizeBytes === 0) return "0B";

    const sizeNames = ["B", "KB", "MB", "GB"];
    let i = 0;

    while (sizeBytes >= 1024 && i < sizeNames.length - 1) {
        sizeBytes /= 1024;
        i++;
    }

    return `${sizeBytes.toFixed(1)}${sizeNames[i]}`;
}

// Utility: show result messages
function showResult(container, type, message, loading = false) {
    if (!container) return;

    let color;
    switch (type) {
        case 'success': color = '#28a745'; break;
        case 'error': color = '#dc3545'; break;
        case 'info': color = '#17a2b8'; break;
        default: color = '#666'; break;
    }

    container.innerHTML = `<div style="color: ${color};">${message}${loading ? ' ⏳' : ''}</div>`;
}

// Download steganographic image
async function downloadSteganographicImage(imageId) {
    try {
        console.log(`📥 Downloading steganographic image for ID: ${imageId}`);
        
        // Create download link
        const downloadUrl = `/api/download/${imageId}`;
        
        // Create a temporary link element and trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = `steganographic_${imageId}.png`;
        link.style.display = 'none';
        
        // Add to DOM, click, and remove
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('✅ Download initiated successfully');
        
    } catch (error) {
        console.error('❌ Download failed:', error);
        alert('Failed to download steganographic image. Please try again.');
    }
}

// Get user analytics
async function getUserAnalytics() {
    const address = document.getElementById('analyticsAddress').value;
    const analyticsDiv = document.getElementById('userAnalytics');
    
    if (!address) {
        analyticsDiv.innerHTML = '<div style="color: #dc3545;">Please enter an Ethereum address</div>';
        return;
    }
    
    if (!address.startsWith('0x') || address.length !== 42) {
        analyticsDiv.innerHTML = '<div style="color: #dc3545;">Invalid Ethereum address format</div>';
        return;
    }
    
    try {
        analyticsDiv.innerHTML = '<div style="color: #17a2b8;">Loading user analytics...</div>';
        
        const response = await fetch(`/api/user-images/${address}`);
        const data = await response.json();
        
        if (response.ok) {
            analyticsDiv.innerHTML = `
                <div style="color: #28a745;">
                    <h4>User Analytics</h4>
                    <p><strong>Total Images:</strong> ${data.imageCount}</p>
                    <p><strong>Image IDs:</strong></p>
                    <ul style="margin-left: 20px;">
                        ${data.imageIds.map(id => `<li>${id}</li>`).join('')}
                    </ul>
                </div>
            `;
        } else {
            analyticsDiv.innerHTML = `<div style="color: #dc3545;">Error: ${data.error}</div>`;
        }
    } catch (error) {
        console.error('Analytics error:', error);
        analyticsDiv.innerHTML = '<div style="color: #dc3545;">Failed to load analytics</div>';
    }
}
