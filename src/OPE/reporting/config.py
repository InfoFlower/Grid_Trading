import os
from dotenv import load_dotenv
load_dotenv()
WD = os.getenv('WD')

REPORTING_LOG_PATH = f'{WD}src/OPE/reporting/BACKTESTS/'