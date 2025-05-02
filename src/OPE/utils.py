from dotenv import load_dotenv
import os
load_dotenv()
WD = os.getenv('WD')

def get_dict_order(table):
    dict_to_ret = []
    with open(WD+f'src/OPE/reporting/data_logger/{table}', 'r') as f:
        lines = f.readlines()
        header = True
        for line in lines:
            if header :
                head = line.replace('\n','').split(',')
                header = False
            else:
                TempDict = {key : value for key, value in zip(head,line.split(','))}
                dict_to_ret.append(TempDict)
    return dict_to_ret
