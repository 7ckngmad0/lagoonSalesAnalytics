from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
import os
from pathlib import Path
from analysis import analyze_dataset
from data_cleaning import clean_dataset
from generate_charts import generate_charts
import io
from datetime import datetime
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure data folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store current dataframe in session-like variable
current_data = {'df': None, 'cleaned_df': None, 'file_name': None}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Read the file
        df = pd.read_csv(file)
        current_data['df'] = df
        current_data['file_name'] = file.filename
        
        # Get basic info
        info = {
            'file_name': file.filename,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'preview': df.astype(str).to_dict('records')
        }
        
        return jsonify({'success': True, 'data': info})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/clean-data', methods=['POST'])
def clean_data():
    try:
        if current_data['df'] is None:
            return jsonify({'error': 'No data loaded'}), 400
        
        # Save temporarily and clean
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.csv')
        current_data['df'].to_csv(temp_path, index=False)
        
        cleaned_df = clean_dataset(temp_path)
        current_data['cleaned_df'] = cleaned_df
        
        # Generate charts
        generate_charts(cleaned_df)
        
        info = {
            'success': True,
            'original_rows': len(current_data['df']),
            'cleaned_rows': len(cleaned_df),
            'removed_rows': len(current_data['df']) - len(cleaned_df),
            'preview': cleaned_df.astype(str).to_dict('records')
        }
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze', methods=['GET'])
def analyze():
    try:
        df_to_analyze = current_data['cleaned_df'] if current_data['cleaned_df'] is not None else current_data['df']
        
        if df_to_analyze is None:
            return jsonify({'error': 'No data loaded'}), 400
        
        # Save to temp file and analyze
        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_analyze.csv')
        df_to_analyze.to_csv(temp_path, index=False)
        
        results = analyze_dataset(temp_path)
        
        # Convert results to JSON-serializable format
        def convert_to_serializable(obj):
            """Convert numpy/pandas types to JSON-serializable Python types"""
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, pd.Series):
                return {str(k): convert_to_serializable(v) for k, v in obj.to_dict().items()}
            elif isinstance(obj, pd.DataFrame):
                return obj.astype(str).to_dict('records')
            elif isinstance(obj, dict):
                return {str(k): convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            elif pd.isna(obj):
                return None
            else:
                return obj

        json_results = {key: convert_to_serializable(value) for key, value in results.items()}
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return jsonify(json_results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    try:
        charts_dir = 'static/charts'
        if not os.path.exists(charts_dir):
            return jsonify({'error': 'No charts available'}), 400
        
        # Get list of generated chart files
        chart_files = {}
        for file in os.listdir(charts_dir):
            if file.endswith('.png'):
                chart_name = file.replace('.png', '')
                chart_files[chart_name] = f'/static/charts/{file}'
        
        return jsonify(chart_files)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-cleaned', methods=['GET'])
def download_cleaned():
    try:
        if current_data['cleaned_df'] is None:
            return jsonify({'error': 'No cleaned data available'}), 400
        
        output = io.BytesIO()
        current_data['cleaned_df'].to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'lagoon_sales_cleaned_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sample-data', methods=['GET'])
def get_sample_data():
    try:
        sample_path = 'data/lagoon_sales_mock.csv'
        if os.path.exists(sample_path):
            df = pd.read_csv(sample_path)
            current_data['df'] = df
            current_data['file_name'] = 'lagoon_sales_mock.csv'
            
            info = {
                'file_name': 'Sample Data Loaded',
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'preview': df.head(5).to_dict('records')
            }
            return jsonify({'success': True, 'data': info})
        else:
            return jsonify({'error': 'Sample data not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dataset-info', methods=['GET'])
def get_dataset_info():
    try:
        df = current_data['cleaned_df'] if current_data['cleaned_df'] is not None else current_data['df']
        
        if df is None:
            return jsonify({'error': 'No data loaded'}), 400
        
        # Get memory usage
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024  # in MB
        
        # Get column information
        column_info = {}
        for col in df.columns:
            column_info[col] = {
                'type': str(df[col].dtype),
                'non_null': int(df[col].notna().sum()),
                'unique': int(df[col].nunique()),
                'null_count': int(df[col].isna().sum())
            }
        
        return jsonify({
            'rows': len(df),
            'columns': len(df.columns),
            'file_name': current_data['file_name'],
            'memory_usage': f'{memory_usage:.2f} MB',
            'column_info': column_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/raw-data', methods=['GET'])
def get_raw_data():
    try:
        if current_data['df'] is None:
            return jsonify({'error': 'No raw data loaded'}), 400
        
        df = current_data['df']
        # Limit to first 1000 rows for performance
        data = df.head(1000).astype(str).to_dict('records')
        columns = list(df.columns)
        
        return jsonify({
            'data': data,
            'columns': columns,
            'total_rows': len(df)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cleaned-data', methods=['GET'])
def get_cleaned_data():
    try:
        if current_data['cleaned_df'] is None:
            return jsonify({'error': 'No cleaned data available'}), 400
        
        df = current_data['cleaned_df']
        # Limit to first 1000 rows for performance
        data = df.head(1000).astype(str).to_dict('records')
        columns = list(df.columns)
        
        return jsonify({
            'data': data,
            'columns': columns,
            'total_rows': len(df)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-charts', methods=['POST'])
def generate_new_charts():
    try:
        if current_data['cleaned_df'] is None:
            return jsonify({'error': 'No cleaned data available'}), 400
        
        # Generate charts
        generate_charts(current_data['cleaned_df'])
        
        return jsonify({'success': True, 'message': 'Charts generated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
