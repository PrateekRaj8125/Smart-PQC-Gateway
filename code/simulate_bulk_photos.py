import os
import requests
import time
import io
import random

SERVER_URL = "http://127.0.0.1:5000"
TOTAL_PHOTOS = 1000

def generate_photo():
    """Simulates a high-res smartphone photo (1.5MB to 3.5MB)"""
    size_mb = random.uniform(1.5, 3.5)
    size_bytes = int(size_mb * 1024 * 1024)
    return io.BytesIO(os.urandom(size_bytes)), round(size_mb, 2)

def run_photo_backup():
    print(f"📸 Initializing Cloud Backup for {TOTAL_PHOTOS} Photos...")
    
    try:
        clumsy_lag = float(input("Enter current Clumsy Lag (ms) [Press Enter for 0]: ") or 0.0)
        clumsy_drop = float(input("Enter current Clumsy Drop (%) [Press Enter for 0]: ") or 0.0)
    except ValueError:
        clumsy_lag = 0.0
        clumsy_drop = 0.0

    print("\n🚀 Beginning Upload...")
    
    start_time_total = time.perf_counter()
    pqc_count = 0
    aes_count = 0
    total_data_mb = 0

    for i in range(1, TOTAL_PHOTOS + 1):
        photo_obj, size_mb = generate_photo()
        total_data_mb += size_mb
        
        start_time_req = time.perf_counter()
        
        try:
            response = requests.post(
                f"{SERVER_URL}/upload_file",
                files={'file': (f'IMG_{i:04d}.jpg', photo_obj)},
                data={
                    'username': 'Mobile_User_Backup',
                    'dataType': 'High_Res_Image',
                    'clumsyLag': clumsy_lag,
                    'clumsyDrop': clumsy_drop,
                    'algoSelect': 'Automatic'  # <-- Added the required dropdown value here!
                }
            )
            
            end_time_req = time.perf_counter()
            real_time_ms = round((end_time_req - start_time_req) * 1000, 2)
            
            if response.status_code == 200:
                res_json = response.json()
                algo = res_json.get('algorithm')
                upload_id = res_json.get('upload_id')
                
                if upload_id:
                    requests.post(
                        f"{SERVER_URL}/log_real_time",
                        json={'upload_id': upload_id, 'real_time_ms': real_time_ms}
                    )
                
                if "PQC" in algo:
                    pqc_count += 1
                    algo_tag = "🔴 PQC (THREAT DETECTED)"
                else:
                    aes_count += 1
                    algo_tag = "🟢 AES"
                    
                print(f"[{i}/{TOTAL_PHOTOS}] Uploaded IMG_{i:04d}.jpg ({size_mb} MB) -> {algo_tag} | {real_time_ms} ms")
                
        except requests.exceptions.ConnectionError:
            print(f"[{i}/{TOTAL_PHOTOS}] ❌ Connection Failed.")
            break
            
        time.sleep(0.05) 

    end_time_total = time.perf_counter()
    total_minutes = round((end_time_total - start_time_total) / 60, 2)

    print("\n" + "="*40)
    print("✅ BACKUP COMPLETE")
    print("="*40)
    print(f"Total Photos   : {TOTAL_PHOTOS}")
    print(f"Total Data     : {round(total_data_mb, 2)} MB")
    print(f"Time Taken     : {total_minutes} Minutes")
    print(f"AES Fast Lane  : {aes_count} photos")
    print(f"PQC Secure Lane: {pqc_count} photos")

if __name__ == "__main__":
    run_photo_backup()