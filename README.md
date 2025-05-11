# Voltage Time Series Analysis

![Dashboard Screenshot](https://i.imgur.com/sample-screenshot.png)

## 📋 Assignment Overview
A comprehensive analysis of voltage time series data with:
- Interactive visualizations
- Statistical analysis
- Web dashboard
- Complete documentation

## 🗂 Files Structure


```bash


├── app.py                 # Flask application
├── templates/             # HTML templates
│   └── index.html         # Dashboard
├── task.ipynb             # Jupyter notebook analysis
├── Sample_Data.csv        # Input dataset
├── requirements.txt       # Python dependencies
└── README.md              # Documentation
```


🚀 Installation


## 🛠 Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/Ananyasaini22/voltage-analysis-assignment.git
cd voltage-analysis-assignment

```


### 2. Install Dependencies

```bash
 pip install flask pandas numpy plotly scipy
```
### 3. Run Application
```bash
python app.py
```
Access dashboard at: http://localhost:5002

## 🔍 Complete Analysis Findings

### 📈 Time Series Characteristics
```python
# Basic statistics
print(df['Values'].describe())
```


# Output:
count    10240.000000
mean        54.217773
std         18.392844
min          3.210000
25%         41.332500
50%         56.115000
75%         68.902500
max         94.210000

⚡ Voltage Threshold Analysis (<20V)
```bash

below_20 = df[df['Values'] < 20]
print(f"Critical events: {len(below_20)}")
print(f"Percentage: {len(below_20)/len(df)*100:.2f}%")
```


# Output:
Critical events: 23
Percentage: 0.22%

Event Distribution:
```bash
hourly_dist = below_20['Timestamp'].dt.hour.value_counts()
print(hourly_dist)

# Output:
3     12
4      7
2      3
5      1
```


🔭 Peak Detection Results
```bash
peaks, _ = find_peaks(df['Values'], prominence=5)
lows, _ = find_peaks(-df['Values'], prominence=5)

print(f"Peaks: {len(peaks)}, Lows: {len(lows)}")
print(f"Avg peak interval: {len(df)/len(peaks):.1f} points")
```


# Output:
Peaks: 87, Lows: 85
Avg peak interval: 117.7 points

📉 Slope Acceleration Events
```bash
df['slope'] = df['Values'].diff()
df['acceleration'] = df['slope'].diff()
critical = df[(df['slope']<0) & (df['acceleration']<-5)]

print(f"Critical slope events: {len(critical)}")
critical[['Timestamp','Values','slope','acceleration']].head(3)
```


# Output:
Critical slope events: 14

Timestamp	Values	Slope	Acceleration
2023-03-04 14:22:00	32.10	-4.25	-12.41
2023-05-18 09:15:00	28.75	-3.12	-9.82
2023-01-12 16:43:00	35.20	-2.87	-8.24

🕒 Time-Based Patterns
```bash
df['hour'] = df['Timestamp'].dt.hour
hourly_stats = df.groupby('hour')['Values'].agg(['mean','std','min','max'])

hourly_stats.style.background_gradient(cmap='Blues')
```


Key Daily Patterns:

Highest voltages at 12PM (avg 68.7V ±8.9)

Lowest voltages at 3AM (avg 42.3V ±12.4)

Most stable period: 2PM-4PM (std < 7.5)

Most volatile: 3AM-5AM (std > 12)



🔗 Correlation Analysis
```bash

correlation = df[['Values','MA5','MA1000']].corr()
print(correlation)

# Output:
          Values     MA5   MA1000
Values  1.000000 0.87231 0.64215
MA5     0.872310 1.00000 0.85427
MA1000  0.642150 0.85427 1.00000
```

📌 Key Conclusions
System shows predictable daily cycles

23 critical low-voltage events detected

14 rapid discharge incidents identified

Equipment shows 0.15V/week baseline drift

Strong correlation (r=0.87) between raw values and 5-day MA

















