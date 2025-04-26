from datetime import datetime

class know_your_perf:
    def __init__(self, sniffing_name='Main Backtest', perf_csv='perf.csv',verbose=False):
        self.verbose = verbose
        self.start_time = datetime.now()
        self.iteration_count = 0
        self.last_step_time = datetime.now()
        self.perf_csv = perf_csv
        self.sniffing_name = sniffing_name
        
    
    def __call__(self):
        self.iteration_count += 1
        self.actual_time = datetime.now()
        with open(self.perf_csv, 'a') as f:
            f.write(f'\n{self.sniffing_name},{self.start_time},{self.last_step_time},{self.actual_time},{self.actual_time-self.start_time},{self.actual_time-self.last_step_time}, {self.iteration_count}'
        )