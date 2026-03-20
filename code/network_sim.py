import random
import time

def simulate_transmission(ciphertext, algo_name):
    # Calculate file size based on actual encrypted payload
    size_kb = len(ciphertext) / 1024.0
    base_latency_ms = 15.0 
    
    # Apply cryptographic network penalties
    if "PQC" in algo_name:
        loss_probability = 0.08  # 8% baseline loss chance due to massive header
        latency_multiplier = 1.5 # 50% slower processing
    else:
        loss_probability = 0.02  # 2% baseline loss chance
        latency_multiplier = 1.0

    actual_latency = base_latency_ms + (size_kb * latency_multiplier)
    
    # Simulate dropped packets
    packets_lost = 0
    if random.random() < loss_probability:
        packets_lost = random.randint(1, max(2, int(size_kb / 10)))
        
    # Artificial sleep to mimic real-world network transit
    time.sleep(min(actual_latency / 1000.0, 2.0)) 
    
    delivery_success_rate = max(0.0, 100.0 - (packets_lost * 0.5))

    return {
        "file_size_kb": round(size_kb, 2),
        "latency_ms": round(actual_latency, 2),
        "packets_lost": packets_lost,
        "delivery_success_rate": round(delivery_success_rate, 2)
    }