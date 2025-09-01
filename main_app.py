from flask import Flask, send_from_directory, request, jsonify
from pathlib import Path
import uuid
import json
import os
from dotenv import load_dotenv
import threading
from main import main
load_dotenv()
WD = os.getenv('WD')
for i in os.listdir(WD+'200_WebServer/WEB/temp'):
    os.remove(WD+'src/WEB/temp/'+i)
app = Flask(__name__)
port = 5000
# Absolute path to base directory and public directory
BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / 'WEB' / 'public'
DATA_DIR = '../data/'

class cache:
    def __init__(self):
        self.cache_data={}

cache=cache()
# === Static Routes ===

@app.route('/')
def home():
    cache.cache_data={}
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

# == Intern API ==

@app.route('/put_data/<path:key>/<path:value>')
def put_data(key,value):
    cache.cache_data[key]=value
    try :
        with open(WD + '200_WebServer/WEB/memory/last_cache.json','w') as f : f.write(json.dumps(cache.cache_data))
    except Exception as e:
        print(f'Error : {e}')
    return jsonify({
        'status':'Logged',
        'Current_cache':cache.cache_data
    })


@app.route('/get_data/<path:key>')
def get_data(key):
    try: return jsonify({'response' : cache.cache_data[key]})
    except Exception as err : return jsonify({'response': str(err)})
# === Backtest Endpoint ===

@app.route('/LaunchBacktest', methods=['POST'])
def launch_backtest():
    try:
        cache.cache_data['task_id'] = str(uuid.uuid4())
        data = request.get_json()
        thread = threading.Thread(target=launch_backtest, args=(data,))
        thread.start()
        return jsonify({'status' : 'launched', 'uuid':cache.cache_data['task_id']})
    except Exception as e:
        print(e)
        return jsonify({"status": "error", "message": str(e), "code": 500}), 500

def launching_backtest(data):
    print('lauching')
    result = main(data)
    result.main(cache.cache_data['task_id'])
# === Reporting Endpoint (placeholder) ===

# @app.route('/ReportingData')
# def load_reporting():
#     from OPE.utils import get_dict_order
#     try :
#         data = {
#             'orders':get_dict_order('Order.csv'),
#             'positions':get_dict_order('Position.csv')}
#         return jsonify({"status": "success","data":data,"code":200}),200
#     except json.JSONDecodeError :
#         return jsonify({"status": "error", "message": "Invalid JSON", "code": 400}), 400
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e), "code": 500}), 500

# @app.route('/GetCurve/<path:data_file>/<path:position_file>')
# def load_curve(data_file,position_file):
#     from OPE.reporting.app.Make_Equity  import plot_equity_curve
#     if len(data_file.split('_'))>3:
#         data_file = WD + 'data/OPE_DATA/DATA_RAW_S_ORIGIN_test_code/' + data_file
#     else :
#         data_file = WD + 'data/DATA_RAW_S_ORIGIN/' + data_file
#     position_file = WD + '200_WebServer/OPE/reporting/data_logger/' + position_file
#     fig = plot_equity_curve(data_file, position_file)
#     return jsonify({'equity_curve':fig})
    
# # == Make a full graph ==
# #/full_graph//<path:order_file>/<path:position_file>
# @app.route('/full_graph')
# def make_full_graph():
#     from OPE.reporting.app.make_full_graph import get_data_graph
#     cache.cache_data['datafile']='data_raw_BTCUSDT'
#     return jsonify(get_data_graph(f'{cache.cache_data["datafile"]}.csv',f'{WD}200_WebServer/OPE/reporting/data_logger/Order.csv',f'{WD}200_WebServer/OPE/reporting/data_logger/Position.csv'))

# # === Run the app ===

if __name__ == '__main__':
    print(f"\nFlask server running on http://localhost:{port}")
    print(f"- Home:    http://localhost:{port}/")
    print(f"- Setup:   http://localhost:{port}/public/setup/setup_page.html\n")
    app.run()