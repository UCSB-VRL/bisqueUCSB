import os

source_dir = '../source/'

py_files = list()


for root, dirs, files in os.walk(source_dir):
    for f in files:
        if f.endswith('.py'):
            py_files.append(os.path.join(root,f))


pylons_files = list()

pylons_lines = dict()

for f in py_files:
    with open(f) as fil: lines = fil.read().split('\n')
    pylons_lines[f] = [(i,l) for i,l in enumerate(lines) if "pylons" in l.split('#')[0].lower()]


for k,v in pylons_lines.items():
    if len(v) > 0:
        pylons_files.append(k)
        print(k,'\n')
        for i, l in v:
            print(i, '\t', l)
        print('\n')


print('Files with pylons:',len(pylons_files))
print('Total python files:',len(py_files))


pylons_all = {i[1] for l in pylons_lines.values() for i in l}

print(pylons_all)

pylons_imports = {i for i in pylons_all if "import" in i}
pylons_other = pylons_all - pylons_imports








