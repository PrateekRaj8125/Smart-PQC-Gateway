import os
import requests
import time
import io

SERVER_URL = "http://127.0.0.1:5000"

def generate_dummy_file(size_kb):
    size_bytes = int(size_kb * 1024)
    return io.BytesIO(os.urandom(size_bytes))

def run_automated_tests():
    print("🤖 Initializing Research Automator Bot...")
    print(f"Targeting server: {SERVER_URL}")
    
    print("\n--- Network Degradation Settings ---")
    try:
        clumsy_lag = float(input("Enter current Clumsy Lag (ms) [Press Enter for 0]: ") or 0.0)
        clumsy_drop = float(input("Enter current Clumsy Drop (%) [Press Enter for 0]: ") or 0.0)
    except ValueError:
        clumsy_lag = 0.0
        clumsy_drop = 0.0
        
    payload_profiles = [
        {"type": "Text_IoT",       "size_kb": 1.0,     "iterations": 1000},
        {"type": "Document_PDF",   "size_kb": 50.0,    "iterations": 500},
        {"type": "High_Res_Image", "size_kb": 2500.0,  "iterations": 500},
        {"type": "HD_Video",       "size_kb": 10000.0, "iterations": 500}
    ]
    
    total_tests = sum(profile["iterations"] for profile in payload_profiles)
    print(f"\nExecuting {total_tests} total uploads across different data categories.")
    
    current_test = 0

    for profile in payload_profiles:
        p_type = profile["type"]
        p_size = profile["size_kb"]
        p_iters = profile["iterations"]
        
        print(f"--- 📦 Starting batch for {p_type} ({p_size} KB) ---")
        
        for i in range(p_iters):
            current_test += 1
            file_obj = generate_dummy_file(p_size)
            start_time = time.perf_counter()
            
            try:
                response = requests.post(
                    f"{SERVER_URL}/upload_file",
                    files={'file': (f'{p_type}_data.bin', file_obj)},
                    data={
                            'username': f'AutoBot_{p_type}', 
                            'dataType': p_type, 
                            'clumsyLag': clumsy_lag, 
                            'clumsyDrop': clumsy_drop,
                            'algoSelect': 'Automatic'  # <--- Add this!
                        }
                )
                
                end_time = time.perf_counter()
                real_time_ms = round((end_time - start_time) * 1000, 2)
                
                if response.status_code == 200:
                    res_json = response.json()
                    algo = res_json.get('algorithm')
                    if not algo: continue

                    upload_id = res_json.get('upload_id')
                    if upload_id:
                        requests.post(f"{SERVER_URL}/log_real_time", json={'upload_id': upload_id, 'real_time_ms': real_time_ms})
                    
                    algo_short = "PQC" if "PQC" in algo else "AES"
                    print(f"[{current_test}/{total_tests}] {p_type} | {algo_short} | Time: {real_time_ms} ms")
                else:
                    print(f"[{current_test}/{total_tests}] ❌ HTTP {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print(f"[{current_test}/{total_tests}] ❌ CONNECTION FAILED.")
                return
            
            time.sleep(0.05) 

    print("\n✅ Testing complete! Refresh your web dashboard.")

if __name__ == "__main__":
    run_automated_tests()