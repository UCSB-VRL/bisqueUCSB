# Install script for BotanicamTrainer
import sys
from bq.setup.module_setup import matlab_setup, read_config, ensure_binary

def setup(params, *args, **kw):
    ensure_binary('svm-predict')
    ensure_binary('svm-scale')       
    return matlab_setup('BotanicamTrainer', params=params)
    
if __name__ =="__main__":
    params = read_config('runtime-bisque.cfg')
    if len(sys.argv)>1:
        params = eval (sys.argv[1])

    sys.exit(setup(params))
