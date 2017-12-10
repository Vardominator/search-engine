import time
import os
import numpy as np
import pandas
from bokeh.plotting import figure, output_file, show
from diskindex import Spimi

start = 10
end = 100000000
blocksizes = np.logspace(1, 8, num=8)
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
        elapsed = blocksize * 2
        f.write('{},{}\n'.format(blocksize, elapsed))

df = pandas.read_csv('{}/blocksize_time.csv'.format(path))
x = df.time
y = df.blocksize

p = figure(
    tools="pan,box_zoom,reset,save",
    title="Blocksize vs Time",
    x_axis_label="Time",
    y_axis_label="Blocksize",
    y_axis_type="log"
)

p.line(x, y, line_width=1)
p.scatter(x=x, y=y)
output_file('{}/blocksize_time.html'.format(path))
show(p)