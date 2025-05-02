import eventlet
eventlet.monkey_patch()  # Required for eventlet to work properly

from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO, emit
from pathlib import Path
import json
import os
from dotenv import load_dotenv
load_dotenv()
WD = os.getenv('WD')

app = Flask(__name__)
port = 3000
socketio = SocketIO(app, cors_allowed_origins="*")
# Absolute path to base directory and public directory
BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / 'WEB' / 'public'
DATA_DIR = '../data/'

cache_data={}

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
            return jsonify({'error': f'File not found | Path searched :{file_path/filename}'}), 404
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

@app.route('/put_data/<path:key>/<path:value>')
def put_data(key,value):
    cache_data[key]=value
    with open('memory/last_cache.json','w') as f : f.write(str(jsonify(cache_data)))
    return jsonify({
        'status':'Logged',
        'Current_cache':cache_data
    })

@app.route('/get_data/<path:key>')
def get_data(key):
    return jsonify({'response' : cache_data[key]})
# === Backtest Endpoint ===

# @app.route('/LaunchBacktest', methods=['POST'])
# def launch_backtest():
#     from main import main
#     try:
#         data = request.get_json()
#         result = main(data)
#         return jsonify({"status": "success", "message": "Backtest executed", "code": 200}), 200
#     except json.JSONDecodeError:
#         return jsonify({"status": "error", "message": "Invalid JSON", "code": 400}), 400
#     except Exception as e:
#         print(e)
#         return jsonify({"status": "error", "message": str(e), "code": 500}), 500

# === Reporting Endpoint (placeholder) ===

@app.route('/ReportingData')
def load_reporting():
    from OPE.utils import get_dict_order
    try :
        data = {
            'orders':get_dict_order('Order.csv'),
            'positions':get_dict_order('Position.csv')}
        return jsonify({"status": "success","data":data,"code":200}),200
    except json.JSONDecodeError :
        return jsonify({"status": "error", "message": "Invalid JSON", "code": 400}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "code": 500}), 500

@app.route('/GetCurve/<path:data_file>/<path:position_file>')
def load_curve(data_file,position_file):
    from OPE.reporting.app.Make_Equity  import plot_equity_curve
    if len(data_file.split('_'))>3:
        data_file = WD + 'data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/' + data_file
    else :
        data_file = WD + 'data/DATA_RAW_S_ORIGIN/' + data_file
    position_file = WD + 'src/OPE/reporting/data_logger/' + position_file
    fig = plot_equity_curve(data_file, position_file)
    return jsonify({'equity_curve':fig})
    
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('message', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('start_backtest')
def handle_backtest(data):
    try:
        from main import main
        emit('message', {'type': 'progress', 'message': 'Backtest starting...'})
        result = main(data, emit=emit)

        emit('close', {'message': 'Closing connection...'})
    except Exception as e:
        emit('message', {'type': 'error', 'message': str(e)})

# === Run the app ===

if __name__ == '__main__':
    print(f"\nFlask server running on http://localhost:{port}")
    print(f"- Home:    http://localhost:{port}/")
    print(f"- Setup:   http://localhost:{port}/public/setup/setup_page.html\n")
    socketio.run(app, host='0.0.0.0', port=3000, debug=True)