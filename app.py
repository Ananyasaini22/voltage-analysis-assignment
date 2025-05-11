from flask import Flask, render_template, send_file
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.io as pio
from scipy.signal import find_peaks
import os
from datetime import datetime
import io

app = Flask(__name__)

# Constants
VOLTAGE_THRESHOLD = 20
SLOPE_ACCEL_THRESHOLD = -5
MA_WINDOW = 5

def process_data():
    """Process data and return all analysis results"""
    file_path = os.path.join(os.path.dirname(__file__), 'Sample_Data.csv')
    if not os.path.exists(file_path):
        raise FileNotFoundError("Data file not found")

    df = pd.read_csv(file_path)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df.dropna(subset=['Timestamp'])

    # Moving averages
    df['MA5'] = df['Values'].rolling(window=MA_WINDOW).mean()
    df['MA1000'] = df['Values'].rolling(window=1000).mean()
    df['MA5000'] = df['Values'].rolling(window=5000).mean()

    # Peaks and lows
    peaks, _ = find_peaks(df['Values'])
    lows, _ = find_peaks(-df['Values'])

    # Voltage < threshold
    below_threshold = df[df['Values'] < VOLTAGE_THRESHOLD]

    # Downward slope acceleration
    df['slope'] = df['Values'].diff()
    df['slope_change'] = df['slope'].diff()
    accelerated_slope = df[(df['slope'] < 0) & (df['slope_change'] < SLOPE_ACCEL_THRESHOLD)]

    return df, peaks, lows, below_threshold, accelerated_slope

def create_plots(df, peaks, lows, below_threshold):
    """Create all required Plotly figures"""
    # Main plot with all MAs
    fig_main = go.Figure()
    fig_main.add_trace(go.Scatter(
        x=df['Timestamp'], y=df['Values'], 
        name='Original Values', line=dict(color='blue')))
    fig_main.add_trace(go.Scatter(
        x=df['Timestamp'], y=df['MA5'], 
        name='5-Day MA', line=dict(color='orange', dash='dot')))
    fig_main.add_trace(go.Scatter(
        x=df['Timestamp'], y=df['MA1000'], 
        name='1000-Point MA', line=dict(color='red')))
    fig_main.add_trace(go.Scatter(
        x=df['Timestamp'], y=df['MA5000'], 
        name='5000-Point MA', line=dict(color='green')))
    fig_main.update_layout(title='Voltage with Moving Averages')

    # Peaks and lows plot
    fig_peaks = go.Figure()
    fig_peaks.add_trace(go.Scatter(
        x=df['Timestamp'], y=df['Values'], 
        name='Voltage', line=dict(color='blue')))
    fig_peaks.add_trace(go.Scatter(
        x=df['Timestamp'].iloc[peaks], y=df['Values'].iloc[peaks], 
        mode='markers', name='Peaks', marker=dict(color='green', size=8)))
    fig_peaks.add_trace(go.Scatter(
        x=df['Timestamp'].iloc[lows], y=df['Values'].iloc[lows], 
        mode='markers', name='Lows', marker=dict(color='red', size=8)))
    fig_peaks.update_layout(title='Local Peaks and Lows')

    # Voltage below threshold plot
    fig_below = go.Figure()
    fig_below.add_trace(go.Scatter(
        x=df['Timestamp'], y=df['Values'], 
        name='Voltage', line=dict(color='blue')))
    fig_below.add_trace(go.Scatter(
        x=below_threshold['Timestamp'], y=below_threshold['Values'], 
        mode='markers', name=f'Below {VOLTAGE_THRESHOLD}', 
        marker=dict(color='orange', size=8)))
    fig_below.update_layout(title=f'Voltage Below {VOLTAGE_THRESHOLD}')

    return fig_main, fig_peaks, fig_below

@app.route('/')
def index():
    try:
        df, peaks, lows, below_threshold, accelerated_slope = process_data()
        fig_main, fig_peaks, fig_below = create_plots(df, peaks, lows, below_threshold)

        # Format timestamps for display
        below_threshold_display = below_threshold.copy()
        below_threshold_display['Timestamp'] = below_threshold_display['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        accelerated_slope_display = accelerated_slope.copy()
        accelerated_slope_display['Timestamp'] = accelerated_slope_display['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

        return render_template('index.html',
            plot_main=pio.to_html(fig_main, full_html=False),
            plot_peaks=pio.to_html(fig_peaks, full_html=False),
            plot_below=pio.to_html(fig_below, full_html=False),
            below_threshold=below_threshold_display.to_dict('records'),
            accelerated_slope=accelerated_slope_display.to_dict('records'),
            ma_window=MA_WINDOW,
            voltage_threshold=VOLTAGE_THRESHOLD,
            slope_threshold=SLOPE_ACCEL_THRESHOLD)

    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/download_csv')
def download_csv():
    """Endpoint to download analysis results as CSV"""
    try:
        df, peaks, lows, below_threshold, accelerated_slope = process_data()
        
        # Create combined CSV
        output = io.StringIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        
        df.to_excel(writer, sheet_name='Full Data')
        df.iloc[peaks][['Timestamp', 'Values']].to_excel(
            writer, sheet_name='Peaks')
        df.iloc[lows][['Timestamp', 'Values']].to_excel(
            writer, sheet_name='Lows')
        below_threshold[['Timestamp', 'Values']].to_excel(
            writer, sheet_name='Below Threshold')
        accelerated_slope[['Timestamp', 'Values', 'slope', 'slope_change']].to_excel(
            writer, sheet_name='Slope Acceleration')
        
        writer.close()
        output.seek(0)
        
        return send_file(
            io.BytesIO(output.getvalue().encode()),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='voltage_analysis.xlsx',
            as_attachment=True
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)