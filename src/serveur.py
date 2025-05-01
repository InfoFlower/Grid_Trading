from flask import Flask, send_from_directory, request, jsonify
from pathlib import Path
import json

app = Flask(__name__)
port = 3000

# Absolute path to base directory and public directory
BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / 'WEB' / 'public'

# === Static Routes ===

@app.route('/')
def home():
    return send_from_directory(PUBLIC_DIR, 'index.html')

@app.route('/public/<path:filename>')
def serve_public_file(filename):
    try:
        SubPath = filename.split('_')[0]
        file_path = PUBLIC_DIR / SubPath
        if not file_path.exists():
            return jsonify({'error': f'File not found | Path searched :{file_path}'}), 404
        return send_from_directory(file_path, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/assets/<path:filename>')
def serve_assets_file(filename):
    try:
        file_path = PUBLIC_DIR/'assets'
        if not file_path.exists():
            return jsonify({'error': f'File not found | Path searched :{file_path}'}), 404
        return send_from_directory(file_path, filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# === Backtest Endpoint ===

@app.route('/LaunchBacktest', methods=['POST'])
def launch_backtest():
    from main import main
    try:
        data = request.get_json()
        result = main(data)
        return jsonify({"status": "success", "message": "Backtest executed", "code": 200}), 200
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "Invalid JSON", "code": 400}), 400
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e), "code": 500}), 500

# === Reporting Endpoint (placeholder) ===

@app.route('/ReportingData')
def load_reporting():
    return jsonify({"status": "not_implemented"}), 501

# === Run the app ===

if __name__ == '__main__':
    print(f"\nFlask server running on http://localhost:{port}")
    print(f"- Home:    http://localhost:{port}/")
    print(f"- Setup:   http://localhost:{port}/public/setup/setup_page.html\n")
    app.run(port=port, debug=True)
