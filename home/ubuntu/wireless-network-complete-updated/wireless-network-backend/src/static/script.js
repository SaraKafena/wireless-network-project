// Configuration - تحديث رابط API حسب بيئة التشغيل
const API_BASE_URL = 'https://wireless-network-project-2.onrender.com'; // للتشغيل المحلي

// DOM Elements
const scenarioCards = document.querySelectorAll('.scenario-card');
const inputForms = document.querySelectorAll('.input-form');
const resultsSection = document.getElementById('results-section');
const loadingOverlay = document.getElementById('loading-overlay');
const calculatedValues = document.getElementById('calculated-values');
const explanationContent = document.getElementById('explanation-content');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeScenarios();
});

// Initialize scenario switching
function initializeScenarios() {
    scenarioCards.forEach(card => {
        card.addEventListener('click', function() {
            const scenario = this.dataset.scenario;
            switchScenario(scenario);
        });
    });
}

// Switch between scenarios
function switchScenario(scenario) {
    scenarioCards.forEach(card => {
        card.classList.remove('active');
        if (card.dataset.scenario === scenario) {
            card.classList.add('active');
        }
    });

    inputForms.forEach(form => {
        form.classList.remove('active');
        if (form.id === `${scenario}-form`) {
            form.classList.add('active');
        }
    });

    resultsSection.style.display = 'none';
}

// Show loading overlay
function showLoading() {
    loadingOverlay.classList.add('active');
}

// Hide loading overlay
function hideLoading() {
    loadingOverlay.classList.remove('active');
}

// Display results
function displayResults(data) {
    calculatedValues.innerHTML = '';
    explanationContent.innerHTML = '';

    if (data.results) {
        Object.entries(data.results).forEach(([key, value]) => {
            const valueItem = document.createElement('div');
            valueItem.className = 'value-item';
            valueItem.innerHTML = `
                <span class="value-label">${formatLabel(key)}</span>
                <span class="value-result">${formatValue(value)}</span>
            `;
            calculatedValues.appendChild(valueItem);
        });
    }

    if (data.explanation) {
        explanationContent.innerHTML = `<p>${data.explanation}</p>`;
    }

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Format label for display
function formatLabel(key) {
    const labelMap = {
        'sampler_output': 'Sampler Output',
        'quantizer_output': 'Quantizer Output',
        'source_encoder_output': 'Source Encoder Output',
        'channel_encoder_output': 'Channel Encoder Output',
        'interleaver_output': 'Interleaver Output',
        'burst_formatting': 'Burst Formatting',
        'data_rate_resource_element': 'Data Rate per Resource Element',
        'bits_per_ofdm_symbol': 'Bits per OFDM Symbol',
        'bits_per_resource_block': 'Bits per Resource Block',
        'max_transmission': 'Max Transmission',
        'spectral_efficiency': 'Spectral Efficiency',
        'max_distance': 'Max Distance',
        'max_cell_size': 'Max Cell Size',
        'number_of_cells': 'Number of Cells',
        'traffic_load_system': 'Traffic Load in Whole System',
        'traffic_load_cell': 'Traffic Load per Cell',
        'cluster_cells': 'Cells per Cluster',
        'transmitted_power_ap': 'Transmitted Power (Access Point)',
        'received_signal_strength_client': 'Received Signal Strength (Client)',
        'transmitted_power_client': 'Transmitted Power (Client)',
        'received_signal_strength_ap': 'Received Signal Strength (Access Point)',
        'free_space_loss': 'Free Space Loss',
        'link_margin_ap_to_client': 'Link Margin (AP to Client)',
        'link_margin_client_to_ap': 'Link Margin (Client to AP)',
        'status': 'Status'
    };
    return labelMap[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Format value for display
function formatValue(value) {
    if (typeof value === 'string') {
        return value;
    }
    if (typeof value === 'number') {
        if (value >= 1000000) {
            return `${(value / 1000000).toFixed(2)} M`;
        } else if (value >= 1000) {
            return `${(value / 1000).toFixed(2)} K`;
        } else {
            return value.toFixed(2);
        }
    }
    return value;
}

// Show error message
function showError(message) {
    alert(`خطأ: ${message}`);
}

// Wireless Communication System Calculation
async function calculateWireless() {
    const data = {
        bandwidth: parseFloat(document.getElementById('bandwidth').value),
        quantization_bits: parseInt(document.getElementById('quantization-bits').value),
        source_encoder_bits: parseFloat(document.getElementById('source-encoder-bits').value),
        channel_encoder: parseFloat(document.getElementById('channel-encoder').value),
        interleaver_bits: parseInt(document.getElementById('interleaver-bits').value),
        block_size: parseInt(document.getElementById('block-size').value),
        overhead_per_block: parseInt(document.getElementById('overhead-per-block').value)
    };

    if (!validateInputs(data)) {
        showError('يرجى ملء جميع الحقول بقيم صحيحة.');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/calculate/wireless`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error:', error);
        showError('فشل في الحساب. يرجى التحقق من الاتصال والمحاولة مرة أخرى.');
    } finally {
        hideLoading();
    }
}

// OFDM Systems Calculation
async function calculateOFDM() {
    const data = {
        bw_resource_block: parseFloat(document.getElementById('bw-resource-block').value),
        subcarrier_spacing: parseFloat(document.getElementById('subcarrier-spacing').value),
        ofdm_symbols: parseInt(document.getElementById('ofdm-symbols').value),
        rb_duration: parseFloat(document.getElementById('rb-duration').value),
        modulated_bits: parseInt(document.getElementById('modulated-bits').value),
        parallel_rb: parseInt(document.getElementById('parallel-rb').value)
    };

    if (!validateInputs(data)) {
        showError('يرجى ملء جميع الحقول بقيم صحيحة.');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/calculate/ofdm`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error:', error);
        showError('فشل في الحساب. يرجى التحقق من الاتصال والمحاولة مرة أخرى.');
    } finally {
        hideLoading();
    }
}

// Link Budget Calculation
async function calculateLinkBudget() {
    const data = {
        access_point_transmit_power: parseFloat(document.getElementById('ap-tx-power').value),
        access_point_antenna_gain: parseFloat(document.getElementById('ap-antenna-gain').value),
        access_point_receive_sensitivity: parseFloat(document.getElementById('ap-rx-sensitivity').value),
        client_transmit_power: parseFloat(document.getElementById('client-tx-power').value),
        client_antenna_gain: parseFloat(document.getElementById('client-antenna-gain').value),
        client_receive_sensitivity: parseFloat(document.getElementById('client-rx-sensitivity').value),
        cable_loss_each_side: parseFloat(document.getElementById('cable-loss-each-side').value),
        distance: parseFloat(document.getElementById('distance').value),
        frequency: parseFloat(document.getElementById('frequency').value)
    };

    if (!validateInputs(data)) {
        showError('يرجى ملء جميع الحقول بقيم صحيحة.');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/calculate/linkbudget`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error:', error);
        showError('فشل في الحساب. يرجى التحقق من الاتصال والمحاولة مرة أخرى.');
    } finally {
        hideLoading();
    }
}

// Cellular System Calculation
async function calculateCellular() {
    const data = {
        time_slots_per_carrier: parseInt(document.getElementById('time-slots-per-carrier').value),
        total_area: parseFloat(document.getElementById('total-area').value),
        max_number_of_users: parseInt(document.getElementById('max-number-of-users').value),
        number_of_calls_per_day: parseInt(document.getElementById('number-of-calls-per-day').value),
        call_duration: parseFloat(document.getElementById('call-duration').value),
        gos: parseFloat(document.getElementById('gos').value),
        sir: parseFloat(document.getElementById('sir').value),
        p0: parseFloat(document.getElementById('p0').value),
        receiver_sensitivity: parseFloat(document.getElementById('receiver-sensitivity').value),
        d0: parseFloat(document.getElementById('d0').value),
        path_loss_exponent: parseFloat(document.getElementById('path-loss-exponent').value),
        co_channel_interferers: parseInt(document.getElementById('co-channel-interferers').value)
    };

    if (!validateInputs(data)) {
        showError('يرجى ملء جميع الحقول بقيم صحيحة.');
        return;
    }

    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/calculate/cellular`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        console.error('Error:', error);
        showError('فشل في الحساب. يرجى التحقق من الاتصال والمحاولة مرة أخرى.');
    } finally {
        hideLoading();
    }
}

// Validate inputs
function validateInputs(data) {
    for (const [key, value] of Object.entries(data)) {
        if (value === null || value === undefined || value === '' || isNaN(value)) {
            return false;
        }
    }
    return true;
}

// Add smooth scrolling for better UX
function smoothScroll(target) {
    document.querySelector(target).scrollIntoView({
        behavior: 'smooth'
    });
}

