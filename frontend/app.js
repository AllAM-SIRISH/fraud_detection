// API Configuration
const API_BASE_URL = '';  // Empty string means same origin (works for deployed apps)

// DOM Elements
const elements = {
    connectionStatus: document.getElementById('connectionStatus'),
    transactionForm: document.getElementById('transactionForm'),
    generateBtn: document.getElementById('generateBtn'),
    predictBtn: document.getElementById('predictBtn'),
    resultsCard: document.getElementById('resultsCard'),
    loadingCard: document.getElementById('loadingCard'),
    predictionStatus: document.getElementById('predictionStatus'),
    riskLevel: document.getElementById('riskLevel'),
    anomalyScore: document.getElementById('anomalyScore'),
    confidence: document.getElementById('confidence'),
    explanation: document.getElementById('explanation')
};

// State
let isServerConnected = false;

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    checkServerConnection();
    setupEventListeners();
});

// Check server connection
async function checkServerConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateConnectionStatus(true, 'Connected');
            isServerConnected = true;
        } else {
            updateConnectionStatus(false, 'Model not ready');
        }
    } catch (error) {
        updateConnectionStatus(false, 'Server offline');
        console.error('Server connection failed:', error);
    }
}

// Update connection status indicator
function updateConnectionStatus(connected, message) {
    const statusDot = elements.connectionStatus.querySelector('.status-dot');
    const statusText = elements.connectionStatus.querySelector('.status-text');
    
    if (connected) {
        statusDot.classList.add('connected');
        statusDot.classList.remove('error');
        statusText.textContent = message;
    } else {
        statusDot.classList.remove('connected');
        statusDot.classList.add('error');
        statusText.textContent = message;
    }
}

// Setup event listeners
function setupEventListeners() {
    elements.generateBtn.addEventListener('click', generateRandomTransaction);
    elements.transactionForm.addEventListener('submit', handlePrediction);
    
    // Reconnect on button click if server is offline
    elements.connectionStatus.addEventListener('click', checkServerConnection);
    elements.connectionStatus.style.cursor = 'pointer';
}

// Generate random transaction
async function generateRandomTransaction() {
    if (!isServerConnected) {
        showError('Server not connected. Please check the backend.');
        return;
    }
    
    try {
        elements.generateBtn.disabled = true;
        elements.generateBtn.textContent = '⏳ Generating...';
        
        const response = await fetch(`${API_BASE_URL}/sample-transaction`);
        
        if (!response.ok) {
            throw new Error('Failed to generate sample transaction');
        }
        
        const transaction = await response.json();
        populateForm(transaction);
        
    } catch (error) {
        console.error('Error generating transaction:', error);
        showError('Failed to generate sample transaction');
    } finally {
        elements.generateBtn.disabled = false;
        elements.generateBtn.textContent = '🎲 Generate Random Transaction';
    }
}

// Populate form with transaction data
function populateForm(transaction) {
    Object.keys(transaction).forEach(key => {
        const input = document.getElementById(key);
        if (input) {
            input.value = transaction[key];
        }
    });
}

// Handle prediction form submission
async function handlePrediction(event) {
    event.preventDefault();
    
    if (!isServerConnected) {
        showError('Server not connected. Please check the backend.');
        return;
    }
    
    const formData = new FormData(elements.transactionForm);
    const transaction = Object.fromEntries(formData.entries());
    
    // Validate form data
    if (!validateTransaction(transaction)) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(transaction)
        });
        
        if (!response.ok) {
            throw new Error('Prediction request failed');
        }
        
        const result = await response.json();
        displayResults(result);
        
    } catch (error) {
        console.error('Prediction error:', error);
        showError('Failed to analyze transaction');
    } finally {
        showLoading(false);
    }
}

// Validate transaction data
function validateTransaction(transaction) {
    const requiredFields = [
        'amount', 'transaction_type', 'account_age_days',
        'location_risk_score', 'device_risk_score',
        'transaction_hour', 'past_transactions_24h'
    ];
    
    for (const field of requiredFields) {
        if (!transaction[field] || transaction[field] === '') {
            showError(`Please fill in the ${field.replace(/_/g, ' ')} field`);
            return false;
        }
    }
    
    // Validate numeric ranges
    const amount = parseFloat(transaction.amount);
    if (amount < 0) {
        showError('Amount must be positive');
        return false;
    }
    
    const locationRisk = parseFloat(transaction.location_risk_score);
    const deviceRisk = parseFloat(transaction.device_risk_score);
    if (locationRisk < 0 || locationRisk > 1 || deviceRisk < 0 || deviceRisk > 1) {
        showError('Risk scores must be between 0 and 1');
        return false;
    }
    
    const hour = parseInt(transaction.transaction_hour);
    if (hour < 0 || hour > 23) {
        showError('Transaction hour must be between 0 and 23');
        return false;
    }
    
    return true;
}

// Show loading state
function showLoading(show) {
    if (show) {
        elements.loadingCard.style.display = 'block';
        elements.resultsCard.style.display = 'none';
        elements.predictBtn.disabled = true;
        elements.predictBtn.textContent = '⏳ Analyzing...';
    } else {
        elements.loadingCard.style.display = 'none';
        elements.predictBtn.disabled = false;
        elements.predictBtn.textContent = '🔍 Analyze Transaction';
    }
}

// Display prediction results
function displayResults(result) {
    const { prediction, anomaly_score, risk_level, explanation } = result;
    
    // Update prediction status
    elements.predictionStatus.className = `prediction-status ${prediction.toLowerCase()}`;
    const statusIcon = elements.predictionStatus.querySelector('.status-icon');
    const statusLabel = elements.predictionStatus.querySelector('.status-label');
    
    if (prediction === 'SAFE') {
        statusIcon.textContent = '✅';
        statusLabel.textContent = 'Transaction Safe';
    } else {
        statusIcon.textContent = '⚠️';
        statusLabel.textContent = 'Potential Fraud';
    }
    
    // Update risk level
    const riskBadge = elements.riskLevel.querySelector('.risk-badge');
    riskBadge.className = `risk-badge ${risk_level.toLowerCase()}`;
    riskBadge.textContent = risk_level;
    
    // Update metrics
    elements.anomalyScore.textContent = anomaly_score.toFixed(4);
    
    // Calculate confidence based on absolute anomaly score
    const confidence = Math.min(Math.abs(anomaly_score) * 100, 99.9);
    elements.confidence.textContent = `${confidence.toFixed(1)}%`;
    
    // Update explanation
    elements.explanation.textContent = explanation;
    
    // Show results card
    elements.resultsCard.style.display = 'block';
    
    // Scroll to results
    elements.resultsCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show error message
function showError(message) {
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.innerHTML = `
        <div class="error-content">
            <span class="error-icon">❌</span>
            <span class="error-message">${message}</span>
            <button class="error-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Add error styles if not already present
    if (!document.querySelector('#error-styles')) {
        const style = document.createElement('style');
        style.id = 'error-styles';
        style.textContent = `
            .error-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border: 1px solid #ef4444;
                border-radius: 0.5rem;
                box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
                z-index: 1000;
                animation: slideInRight 0.3s ease-out;
                max-width: 400px;
            }
            
            .error-content {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 1rem;
            }
            
            .error-icon {
                font-size: 1.25rem;
            }
            
            .error-message {
                flex: 1;
                color: #dc2626;
                font-size: 0.875rem;
            }
            
            .error-close {
                background: none;
                border: none;
                font-size: 1.25rem;
                cursor: pointer;
                color: #6b7280;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .error-close:hover {
                color: #374151;
            }
            
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(errorDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}

// Auto-refresh connection status every 30 seconds
setInterval(checkServerConnection, 30000);
