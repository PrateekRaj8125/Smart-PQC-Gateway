import os
import glob
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import kagglehub
from kagglehub import KaggleDatasetAdapter

DATASET_DIR = kagglehub.dataset_download("chethuhn/network-intrusion-dataset")

def compile_and_train():
    all_files = glob.glob(os.path.join(DATASET_DIR, "*.csv"))
    if not all_files:
        print("❌ Error: No CSV files found in the 'datasets' folder!")
        return
    
    print(f"🔍 Found {len(all_files)} network traffic files. Extracting features...")
    
    # We target the specific flows that define DDoS and PortScans
    features_to_keep = ['Flow Duration', 'Total Fwd Packets', 'Fwd Packet Length Max', 'Flow Bytes/s', 'Label']
    combined_data = []
    
    for file in all_files:
        print(f"   -> Processing {os.path.basename(file)}...")
        try:
            df = pd.read_csv(file, usecols=lambda c: c.strip() in features_to_keep)
            df.columns = df.columns.str.strip()
            combined_data.append(df)
        except Exception as e:
            print(f"   ⚠️ Skipping {file} due to formatting error: {e}")
            
    print("🔄 Merging datasets and handling infinite/NaN values...")
    full_df = pd.concat(combined_data, ignore_index=True)
    full_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    full_df.dropna(inplace=True)
    
    # Isolate features (X) and target labels (y)
    X = full_df[['Flow Duration', 'Total Fwd Packets', 'Fwd Packet Length Max', 'Flow Bytes/s']]
    y = full_df['Label'].apply(lambda x: 0 if x == 'BENIGN' else 1)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    
    print("🧠 Training Random Forest Gateway Router (100 Estimators)...")
    model = RandomForestClassifier(n_estimators=100, max_depth=10, n_jobs=-1, random_state=42)
    model.fit(X_train, y_train)
    
    print("\n📊 --- Academic Validation Metrics ---")
    predictions = model.predict(X_test)
    print(classification_report(y_test, predictions, target_names=['Benign (AES)', 'Attack (Hybrid PQC)']))
    
    joblib.dump(model, 'research_ai_model.pkl')
    print("✅ Model compiled and saved to 'research_ai_model.pkl'")

if __name__ == "__main__":
    compile_and_train()