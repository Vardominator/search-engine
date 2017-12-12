import time
import os
import numpy as np
import pandas
from bokeh.plotting import figure, output_file, show
from diskindex import Spimi


blocksizes = np.logspace(3, 9, num=7)
path = 'data/spimi_analysis'

if not os.path.exists(path):
    os.makedirs(path)

with open('{}/blocksize_time.csv'.format(path), 'w') as f:
    f.write('blocksize,time\n')
    for blocksize in blocksizes:
        print(blocksize)
        start_time = time.time()
        spimi = Spimi(int(blocksize), 'data/script_jsons', '{}/blocks'.format(path))
        end_time = time.time()
        elapsed = end_time - start_time
        print(elapsed)
        f.write('{},{}\n'.format(blocksize, elapsed))
        del spimi

df = pandas.read_csv('{}/blocksize_time.csv'.format(path))
y = df.time
x = df.blocksize

p = figure(
    tools="pan,box_zoom,reset,save",
    title="Time vs Blocksize",
    x_axis_label="Blocksize",
    y_axis_label="Time",
    x_axis_type="log"
)

p.line(x, y, line_width=1)
p.scatter(x=x, y=y)
output_file('{}/blocksize_time.html'.format(path))
show(p)