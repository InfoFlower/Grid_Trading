from concurrent.futures import ThreadPoolExecutor
from main import main
executor = ThreadPoolExecutor(max_workers=1)


result = main('1')
executor.submit(result.main(1))