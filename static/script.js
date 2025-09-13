document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.getElementById('passwordInput');
    const toggleButton = document.getElementById('toggleVisibility');
    const progressFill = document.getElementById('progressFill');
    const scoreValue = document.getElementById('scoreValue');
    const scoreLabel = document.getElementById('scoreLabel');
    const feedback = document.getElementById('feedback');
    const leakedWarning = document.getElementById('leakedWarning');
    const crackTime = document.getElementById('crackTime');
    const timeBarFill = document.getElementById('timeBarFill');
    
    let debounceTimer;
    
    toggleButton.addEventListener('click', function() {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleButton.textContent = '🔒';
        } else {
            passwordInput.type = 'password';
            toggleButton.textContent = '👁️';
        }
    });
    
    passwordInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            checkPasswordStrength(passwordInput.value);
        }, 300);
    });
    
    function checkPasswordStrength(password) {
        if (!password) {
            resetUI();
            return;
        }
        
        fetch('/check_password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password: password })
        })
        .then(response => response.json())
        .then(data => {
            updateUI(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    function updateUI(data) {
        const score = data.score;
        const label = data.label;
        const leaked = data.leaked;
        const feedbackList = data.feedback;
        const crackTimeText = data.crack_time;
        const timeUnit = data.time_unit;
        
        progressFill.style.width = `${score}%`;
        
        if (score < 40) {
            progressFill.style.backgroundColor = '#e53e3e'; // Red
        } else if (score < 60) {
            progressFill.style.backgroundColor = '#ed8936'; // Orange
        } else if (score < 80) {
            progressFill.style.backgroundColor = '#ecc94b'; // Yellow
        } else if (score < 90) {
            progressFill.style.backgroundColor = '#48bb78'; // Green
        } else {
            progressFill.style.backgroundColor = '#38a169'; // Dark green
        }
        
        scoreValue.textContent = score;
        scoreLabel.textContent = label;
        
        scoreLabel.style.color = progressFill.style.backgroundColor;
        
        if (leaked) {
            leakedWarning.classList.remove('hidden');
        } else {
            leakedWarning.classList.add('hidden');
        }
        
        crackTime.textContent = crackTimeText;
        
        let timeBarWidth = 0;
        switch(timeUnit) {
            case "instant":
                timeBarWidth = 5;
                break;
            case "seconds":
                timeBarWidth = 10;
                break;
            case "minutes":
                timeBarWidth = 25;
                break;
            case "hours":
                timeBarWidth = 50;
                break;
            case "days":
                timeBarWidth = 75;
                break;
            case "years":
                timeBarWidth = 100;
                break;
        }
        timeBarFill.style.width = `${timeBarWidth}%`;
        
        if (feedbackList.length > 0) {
            let html = '<p>Untuk meningkatkan keamanan password:</p><ul>';
            feedbackList.forEach(item => {
                html += `<li>${item}</li>`;
            });
            html += '</ul>';
            feedback.innerHTML = html;
        } else {
            feedback.innerHTML = '<p>Password Anda sangat kuat! Pertahankan.</p>';
        }
    }
    
    function resetUI() {
        progressFill.style.width = '0%';
        progressFill.style.backgroundColor = '#e53e3e';
        scoreValue.textContent = '0';
        scoreLabel.textContent = '-';
        scoreLabel.style.color = '#2d3748';
        leakedWarning.classList.add('hidden');
        crackTime.textContent = '-';
        timeBarFill.style.width = '0%';
        feedback.innerHTML = '<p>Masukkan password untuk melihat analisis detail</p>';
    }
});