import sqlite3
import pandas as pd

# Path to your database
DB_PATH = "code/research_data.db"

# Output CSV file
OUTPUT_CSV = "output/research_data.csv"

def convert_db_to_csv():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(DB_PATH)

        # Read table into pandas DataFrame
        query = "SELECT * FROM uploads"
        df = pd.read_sql_query(query, conn)

        # Close connection
        conn.close()

        # Save to CSV
        df.to_csv(OUTPUT_CSV, index=False)

        print(f"✅ Successfully exported {len(df)} records to {OUTPUT_CSV}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    convert_db_to_csv()