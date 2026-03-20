# 📊 Generate Output Notebook (Final - IEEE Ready)
#This notebook:
#- Cleans and processes research data
#- Generates IEEE-ready tables
#- Produces advanced analysis graphs
#- Exports LaTeX tables
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set()

## 📂 Load Dataset
df = pd.read_csv('research_data.csv')
df.columns = df.columns.str.strip()
df.head()

## 🧹 Data Cleaning
df.replace([np.inf, -np.inf], np.nan, inplace=True)
df.dropna(inplace=True)
df['latency_ms'] = df['latency_ms'].round(2)
df['real_latency_ms'] = df['real_latency_ms'].round(2)

## 📊 Table 1: Algorithm Performance
summary = df.groupby('algorithm').agg({
    'latency_ms': ['mean','std'],
    'real_latency_ms':'mean',
    'packets_lost':'mean',
    'size_kb':'mean'
}).reset_index()
summary.columns = ['Algorithm','Sim_Latency_Mean','Sim_Latency_STD','Real_Latency_Mean','Avg_Packet_Loss','Avg_File_Size']
summary
summary.to_csv('tables/table_performance.csv', index=False, float_format='%.2f')

## 📊 Table 2: Payload Latency
payload_table = df.groupby(['data_type','algorithm'])['real_latency_ms'].mean().reset_index()
payload_table
payload_table.to_csv('tables/table_payload.csv', index=False, float_format='%.2f')

## 📊 Table 3: Packet Loss Stats
packet_table = df.groupby('algorithm')['packets_lost'].describe()[['mean','max','min']]
packet_table
packet_table.to_csv('tables/table_packet_loss.csv', float_format='%.2f')


## 📈 Graphs (Formatted - Publication Ready)
## Graph 1: Average Latency
plt.figure()
sns.barplot(data=df, x='algorithm', y='real_latency_ms')
plt.title('Average Network Latency: AES vs PQC')
plt.xlabel('Algorithm')
plt.ylabel('Latency (ms)')
plt.tight_layout()
plt.savefig('charts/fig1_latency_bar.png', dpi=300)

## Graph 2: Latency Scaling
plt.figure()
sns.scatterplot(data=df, x='size_kb', y='real_latency_ms', hue='algorithm')
plt.xscale('log'); plt.yscale('log')
plt.xlabel('File Size (KB)'); plt.ylabel('Latency (ms)')
plt.title('Latency Scaling by Payload Size')
plt.tight_layout()
plt.savefig('charts/fig2_latency_scatter.png', dpi=300)

## Graph 3: Packet Loss
plt.figure()
sns.barplot(data=df, x='algorithm', y='packets_lost')
plt.title('Average Packet Loss Comparison')
plt.tight_layout()
plt.savefig('charts/fig3_packet_loss.png', dpi=300)

## Graph 4: AI Routing Distribution
counts = df['algorithm'].value_counts()
plt.figure()
plt.pie(counts, labels=counts.index, autopct='%1.1f%%')
plt.title('AI Gateway Routing Distribution')
plt.tight_layout()
plt.savefig('charts/fig4_ai_distribution.png', dpi=300)

## Graph 5: Latency Variance
plt.figure()
sns.boxplot(data=df, x='data_type', y='real_latency_ms', hue='algorithm')
plt.yscale('log'); plt.xticks(rotation=30)
plt.title('Latency Variance by Payload Category')
plt.tight_layout()
plt.savefig('charts/fig5_latency_variance.png', dpi=300)

## Graph 6: ECDF
plt.figure()
sns.ecdfplot(data=df, x='real_latency_ms', hue='algorithm')
plt.xscale('log')
plt.title('Empirical Latency Distribution')
plt.tight_layout()
plt.savefig('charts/fig6_latency_ecdf.png', dpi=300)

## Graph 7: Throughput
df['throughput_kbps'] = df['size_kb'] / (df['real_latency_ms']/1000)
plt.figure()
sns.boxplot(data=df, x='algorithm', y='throughput_kbps')
plt.title('Throughput Comparison')
plt.tight_layout()
plt.savefig('charts/fig7_throughput.png', dpi=300)

## Graph 8: Security vs Performance
df['security_score'] = df['algorithm'].apply(lambda x: 10 if 'PQC' in x else 5)
plt.figure()
sns.scatterplot(data=df, x='real_latency_ms', y='security_score', hue='algorithm')
plt.title('Security vs Performance Trade-off')
plt.tight_layout()
plt.savefig('charts/fig8_security_vs_performance_tradeoff.png', dpi=300)