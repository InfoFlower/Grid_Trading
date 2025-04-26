from datetime import datetime

class know_your_perf:
    def __init__(self, sniffing_name, epoch= 500000, perf_csv='src/OPE/technical_report/perfs.csv',verbose=True, is_working=False,truncate=False):
        self.verbose = verbose
        self.start_time = datetime.now()
        self.iteration_count = 0
        self.last_step_time = datetime.now()
        self.perf_csv = perf_csv
        self.sniffing_name = sniffing_name
        self.epoch = epoch
        self.is_working = is_working
        if truncate : 
            with open(self.perf_csv, 'w') as f:
                f.write(f'sniffing_name, start_time, last_step_time, actual_time, duration_bt_start, duration_bt_step, nb_iters\n')
    
    def __call__(self):
        if self.is_working == False: pass
        self.actual_time = datetime.now()
        self.iteration_count += 1
        if self.iteration_count % self.epoch == 0:
            if self.verbose == True:
                Time_since_start = self.actual_time - self.start_time
                Time_since_last_step = self.actual_time - self.last_step_time
                print(f'\n', f'\n','*'*20)
                print(f'Iteration {self.iteration_count} \n Epoch: {self.iteration_count//self.epoch} \n Time since start: {Time_since_start} \n Time since last step: {Time_since_last_step}')
                print(f'\n', f'\n','*'*20)
                self.last_step_time = self.actual_time
            with open(self.perf_csv, 'a') as f:
                f.write(f'\n{self.sniffing_name},{self.start_time},{self.last_step_time},{self.actual_time},{Time_since_start},{Time_since_last_step}, {self.iteration_count}')