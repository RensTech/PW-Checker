from flask import Flask, render_template, request, jsonify
import hashlib
import re
import time
import math

app = Flask(__name__)

# Fungsi untuk memuat hash yang bocor dari file
def load_leaked_hashes():
    try:
        with open('leaked_hashes.txt', 'r') as file:
            return set(line.strip().lower() for line in file)
    except FileNotFoundError:
        return set()

# Fungsi untuk menghitung skor kekuatan password
def calculate_password_strength(password):
    score = 0
    feedback = []
    
    # Panjang password
    length = len(password)
    if length >= 8:
        score += 25
    else:
        feedback.append("Password harus minimal 8 karakter")
    
    # Huruf kecil
    if re.search(r'[a-z]', password):
        score += 10
    else:
        feedback.append("Tambahkan huruf kecil")
    
    # Huruf besar
    if re.search(r'[A-Z]', password):
        score += 10
    else:
        feedback.append("Tambahkan huruf besar")
    
    # Angka
    if re.search(r'[0-9]', password):
        score += 10
    else:
        feedback.append("Tambahkan angka")
    
    # Simbol
    if re.search(r'[^a-zA-Z0-9]', password):
        score += 15
    else:
        feedback.append("Tambahkan simbol")
    
    # Variasi karakter
    char_variety = 0
    if re.search(r'[a-z]', password): char_variety += 1
    if re.search(r'[A-Z]', password): char_variety += 1
    if re.search(r'[0-9]', password): char_variety += 1
    if re.search(r'[^a-zA-Z0-9]', password): char_variety += 1
    
    if char_variety >= 3:
        score += 20
    elif char_variety == 2:
        score += 10
    
    # Panjang tambahan
    if length > 12:
        score += min(10, (length - 12) * 2)
    
    # Pastikan skor antara 0-100
    score = min(100, max(0, score))
    
    # Tentukan label kekuatan
    if score < 40:
        label = "Very Weak"
    elif score < 60:
        label = "Weak"
    elif score < 80:
        label = "Fair"
    elif score < 90:
        label = "Strong"
    else:
        label = "Very Strong"
    
    return score, label, feedback

# Fungsi untuk mengestimasi waktu bruteforce
def estimate_crack_time(password):
    # Karakter set yang mungkin
    char_sets = {
        'lower': 26,    
        'upper': 26,    
        'digits': 10,   
        'symbols': 33   
    }
    
    # Deteksi karakter set yang digunakan
    has_lower = re.search(r'[a-z]', password) is not None
    has_upper = re.search(r'[A-Z]', password) is not None
    has_digits = re.search(r'[0-9]', password) is not None
    has_symbols = re.search(r'[^a-zA-Z0-9]', password) is not None
    
    # Hitung pool size
    pool_size = 0
    if has_lower: pool_size += char_sets['lower']
    if has_upper: pool_size += char_sets['upper']
    if has_digits: pool_size += char_sets['digits']
    if has_symbols: pool_size += char_sets['symbols']
    
    # Jika tidak ada yang terdeteksi, asumsikan hanya lowercase
    if pool_size == 0:
        pool_size = char_sets['lower']
    
    # Hitung kombinasi total
    length = len(password)
    total_combinations = pool_size ** length
    
    # Asumsi: 10^12 percobaan per detik (superkomputer)
    attempts_per_second = 10 ** 12
    
    # Hitung waktu dalam detik
    seconds = total_combinations / (2 * attempts_per_second)  # Dibagi 2 untuk rata-rata
    
    # Konversi ke unit waktu yang sesuai
    if seconds < 1:
        return "segera", "instant"
    elif seconds < 60:
        return "kurang dari 1 menit", "seconds"
    elif seconds < 3600:
        minutes = math.ceil(seconds / 60)
        return f"sekitar {minutes} menit", "minutes"
    elif seconds < 86400:
        hours = math.ceil(seconds / 3600)
        return f"sekitar {hours} jam", "hours"
    elif seconds < 31536000:
        days = math.ceil(seconds / 86400)
        return f"sekitar {days} hari", "days"
    else:
        years = math.ceil(seconds / 31536000)
        return f"sekitar {years} tahun", "years"

# Route utama
@app.route('/')
def index():
    return render_template('index.html')

# API untuk pengecekan password
@app.route('/check_password', methods=['POST'])
def check_password():
    data = request.json
    password = data.get('password', '')
    
    # Hitung kekuatan password
    score, label, feedback = calculate_password_strength(password)
    
    # Cek apakah password bocor
    leaked = False
    if password:
        # Hash password dengan SHA-1
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().lower()
        leaked_hashes = load_leaked_hashes()
        leaked = sha1_hash in leaked_hashes
    
    # Estimasi waktu bruteforce
    crack_time, time_unit = estimate_crack_time(password) if password else ("-", "instant")
    
    # Siapkan respons
    response = {
        'score': score,
        'label': label,
        'leaked': leaked,
        'feedback': feedback,
        'crack_time': crack_time,
        'time_unit': time_unit
    }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)