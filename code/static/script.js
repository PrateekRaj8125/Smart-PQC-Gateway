let latencyChartInstance = null;
let packetLossChartInstance = null;
let pieChartInstance = null;

Chart.defaults.color = '#a9b7c6';
Chart.defaults.borderColor = '#333';

// ==========================================
// CUSTOM DROPDOWN UI LOGIC
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    refreshDashboard();

    const selectWrapper = document.querySelector('.custom-select-wrapper');
    const selectBtn = document.getElementById('customSelectBtn');
    const selectText = document.getElementById('customSelectText');
    const options = document.querySelectorAll('.custom-select-options li');
    const hiddenInput = document.getElementById('algoSelect');

    // Toggle open/close on click
    if (selectBtn) {
        selectBtn.addEventListener('click', () => {
            selectWrapper.classList.toggle('open');
            selectBtn.classList.toggle('open');
        });
    }

    // Handle user selecting an option
    options.forEach(option => {
        option.addEventListener('click', () => {
            options.forEach(opt => opt.classList.remove('selected'));
            option.classList.add('selected');
            
            selectText.innerText = option.innerText;
            hiddenInput.value = option.getAttribute('data-value');
            
            if(hiddenInput.value === 'AES') selectText.style.color = '#2ecc71'; 
            else if(hiddenInput.value === 'PQC') selectText.style.color = '#e74c3c'; 
            else selectText.style.color = '#4CAF50'; 
            
            selectWrapper.classList.remove('open');
            selectBtn.classList.remove('open');
        });
    });

    // Close dropdown if clicked outside
    document.addEventListener('click', (e) => {
        if (selectWrapper && !selectWrapper.contains(e.target)) {
            selectWrapper.classList.remove('open');
            if (selectBtn) selectBtn.classList.remove('open');
        }
    });
});

// ==========================================
// CORE APPLICATION LOGIC
// ==========================================
function updateProgressBar(elementId, value, max) {
    const bar = document.getElementById(elementId);
    const percentage = Math.min((value / max) * 100, 100);
    bar.style.width = `${percentage}%`;

    if (percentage <= 40) {
        bar.style.backgroundColor = '#2ecc71'; 
        bar.style.boxShadow = '0 0 10px #2ecc71';
    } else if (percentage <= 75) {
        bar.style.backgroundColor = '#f1c40f'; 
        bar.style.boxShadow = '0 0 10px #f1c40f';
    } else {
        bar.style.backgroundColor = '#e74c3c'; 
        bar.style.boxShadow = '0 0 10px #e74c3c';
    }
}

document.getElementById('uploadFileBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const textInput = document.getElementById('textPayload');
    const usernameInput = document.getElementById('username');
    const uploadBtn = document.getElementById('uploadFileBtn');
    const algoSelect = document.getElementById('algoSelect'); // Reads the hidden input!
    const timerDisplay = document.getElementById('liveTimerDisplay');
    const actualTimeSpan = document.getElementById('actualTime');

    if (!fileInput.files.length && !textInput.value.trim()) {
        alert("⚠️ Please enter a text message or select a file.");
        return;
    }
    if (!usernameInput.value) {
        alert("⚠️ Please enter a username.");
        return;
    }

    const originalBtnText = uploadBtn.innerText;
    uploadBtn.innerText = "ENCRYPTING & TRANSMITTING... ⏳";
    uploadBtn.disabled = true;
    timerDisplay.style.display = "block";
    actualTimeSpan.innerText = "Measuring...";
    actualTimeSpan.style.color = "#f1c40f"; 

    const formData = new FormData();
    if (fileInput.files.length > 0) formData.append('file', fileInput.files[0]);
    formData.append('textPayload', textInput.value);
    formData.append('username', usernameInput.value);
    formData.append('algoSelect', algoSelect.value); // Sends manual override to Python

    const startTime = performance.now();

    try {
        const response = await fetch('/upload_file', { method: 'POST', body: formData });
        const result = await response.json();
        const endTime = performance.now();
        const realWorldTimeMs = (endTime - startTime).toFixed(2); 

        if (result.status === "success") {
            actualTimeSpan.innerText = realWorldTimeMs;
            actualTimeSpan.style.color = "#2ecc71"; 
            
            await fetch('/log_real_time', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ upload_id: result.upload_id, real_time_ms: parseFloat(realWorldTimeMs) })
            });
            
            document.getElementById('outThreat').innerText = result.threat_level;
            document.getElementById('outLoad').innerText = result.server_load;
            document.getElementById('outAlgo').innerText = result.algorithm;
            document.getElementById('outReason').innerText = result.reason;
            document.getElementById('outCipher').value = result.ciphertext;

            updateProgressBar('threatBar', result.threat_level, 10);
            updateProgressBar('loadBar', result.server_load, 100);

            await refreshDashboard();
        } else {
            alert("❌ Server Error: " + result.error);
            actualTimeSpan.innerText = "Failed";
            actualTimeSpan.style.color = "#e74c3c";
        }
    } catch (error) {
        console.error("Upload failed:", error);
        actualTimeSpan.innerText = "Timeout / Dropped";
        actualTimeSpan.style.color = "#e74c3c";
    } finally {
        uploadBtn.innerText = originalBtnText;
        uploadBtn.disabled = false;
        fileInput.value = ""; 
    }
});

async function refreshDashboard() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        const labels = data.map(row => row[0]); 
        const simLatencyData = data.map(row => row[1].toFixed(2));
        const packetLossData = data.map(row => row[2]);
        const realLatencyData = data.map(row => row[3].toFixed(2));
        const usageCountData = data.map(row => row[4]); 

        renderLatencyChart(labels, simLatencyData, realLatencyData);
        renderPacketLossChart(labels, packetLossData);
        renderPieChart(labels, usageCountData);
    } catch (error) {
        console.error("Failed to load dashboard stats:", error);
    }
}

function renderLatencyChart(labels, simData, realData) {
    const ctx = document.getElementById('latencyChart').getContext('2d');
    if (latencyChartInstance) latencyChartInstance.destroy();

    latencyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                { label: 'Simulated Math (ms)', data: simData, backgroundColor: 'rgba(52, 152, 219, 0.8)' },
                { label: 'Empirical Network (ms)', data: realData, backgroundColor: 'rgba(155, 89, 182, 0.8)' }
            ]
        },
        options: { 
            responsive: true, 
            maintainAspectRatio: false, 
            animation: { duration: 800 } 
        }
    });
}

function renderPacketLossChart(labels, data) {
    const ctx = document.getElementById('packetLossChart').getContext('2d');
    if (packetLossChartInstance) packetLossChartInstance.destroy();

    packetLossChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: { labels: labels, datasets: [{ data: data, backgroundColor: ['#e74c3c', '#f1c40f', '#3498db'] }] },
        options: { 
            responsive: true, 
            maintainAspectRatio: false, 
            animation: { animateScale: true } 
        }
    });
}

function renderPieChart(labels, data) {
    const ctx = document.getElementById('algoPieChart').getContext('2d');
    if (pieChartInstance) pieChartInstance.destroy();

    pieChartInstance = new Chart(ctx, {
        type: 'pie',
        data: { labels: labels, datasets: [{ data: data, backgroundColor: ['#2980b9', '#16a085'] }] },
        options: { 
            responsive: true, 
            maintainAspectRatio: false, 
            animation: { animateScale: true } 
        }
    });
}