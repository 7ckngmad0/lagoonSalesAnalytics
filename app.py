from flask import Flask, render_template, request, jsonify, send_file, Response
import pandas as pd
import json
import os
from analysis import analyze_dataset
from data_cleaning import clean_dataset
import io
from datetime import datetime
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'data'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

current_data = {'df': None, 'cleaned_df': None, 'file_name': None}


def df_to_json_safe(df):
    """Convert dataframe to a JSON string with NaN replaced by null, then parse back to list."""
    return json.loads(df.to_json(orient='records', default_handler=str))


def to_json_response(data):
    """Return a Flask Response with NaN-safe JSON (replaces NaN with null)."""
    text = json.dumps(data, allow_nan=False, default=str)
    return Response(text, mimetype='application/json')


def convert_to_serializable(obj):
    if isinstance(obj, float) and (np.isnan(obj) or np.isinf(obj)):
        return None
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return None if np.isnan(obj) else float(obj)
    elif isinstance(obj, pd.Series):
        return {str(k): convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, pd.DataFrame):
        return df_to_json_safe(obj)
    elif isinstance(obj, dict):
        return {str(k): convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(i) for i in obj]
    return obj


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

        df = pd.read_csv(file)
        current_data['df'] = df
        current_data['file_name'] = file.filename

        info = {
            'success': True,
            'data': {
                'file_name': file.filename,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'preview': df_to_json_safe(df)
            }
        }
        return to_json_response(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clean-data', methods=['POST'])
def clean_data():
    try:
        if current_data['df'] is None:
            return jsonify({'error': 'No data loaded'}), 400

        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp.csv')
        current_data['df'].to_csv(temp_path, index=False)
        cleaned_df = clean_dataset(temp_path)
        current_data['cleaned_df'] = cleaned_df

        if os.path.exists(temp_path):
            os.remove(temp_path)

        info = {
            'success': True,
            'original_rows': len(current_data['df']),
            'cleaned_rows': len(cleaned_df),
            'removed_rows': len(current_data['df']) - len(cleaned_df),
            'preview': df_to_json_safe(cleaned_df)
        }
        return to_json_response(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['GET'])
def analyze():
    try:
        df_to_analyze = current_data['cleaned_df'] if current_data['cleaned_df'] is not None else current_data['df']
        if df_to_analyze is None:
            return jsonify({'error': 'No data loaded'}), 400

        temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_analyze.csv')
        df_to_analyze.to_csv(temp_path, index=False)
        results = analyze_dataset(temp_path)
        if os.path.exists(temp_path):
            os.remove(temp_path)

        json_results = {k: convert_to_serializable(v) for k, v in results.items()}
        return to_json_response(json_results)
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
        return send_file(output, mimetype='text/csv', as_attachment=True,
                         download_name=f'lagoon_sales_cleaned_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sample-data', methods=['GET'])
def get_sample_data():
    try:
        sample_path = 'data/lagoon_sales_mock.csv'
        if not os.path.exists(sample_path):
            return jsonify({'error': 'Sample data not found'}), 404

        df = pd.read_csv(sample_path)
        current_data['df'] = df
        current_data['file_name'] = 'lagoon_sales_mock.csv'

        info = {
            'success': True,
            'data': {
                'file_name': 'Sample Data Loaded',
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'preview': df_to_json_safe(df)
            }
        }
        return to_json_response(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dataset-info', methods=['GET'])
def get_dataset_info():
    try:
        df = current_data['cleaned_df'] if current_data['cleaned_df'] is not None else current_data['df']
        if df is None:
            return jsonify({'error': 'No data loaded'}), 400

        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
        column_info = {
            col: {
                'type': str(df[col].dtype),
                'non_null': int(df[col].notna().sum()),
                'unique': int(df[col].nunique()),
                'null_count': int(df[col].isna().sum())
            }
            for col in df.columns
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
        result = {'data': df_to_json_safe(df.head(1000)), 'columns': list(df.columns), 'total_rows': len(df)}
        return to_json_response(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cleaned-data', methods=['GET'])
def get_cleaned_data():
    try:
        if current_data['cleaned_df'] is None:
            return jsonify({'error': 'No cleaned data available'}), 400
        df = current_data['cleaned_df']
        result = {'data': df_to_json_safe(df.head(1000)), 'columns': list(df.columns), 'total_rows': len(df)}
        return to_json_response(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-charts', methods=['POST'])
def generate_new_charts():
    try:
        if current_data['cleaned_df'] is None:
            return jsonify({'error': 'No cleaned data available'}), 400
        return jsonify({'success': True, 'message': 'Ready to render charts'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)