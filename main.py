from dateutil.parser import isoparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker 
from file_read_backwards import FileReadBackwards
import json
from datetime import datetime
from scipy.interpolate import make_interp_spline, BSpline
import numpy as np

log1 = "./uninterrupted_log.log"
log2 = "./tower_log.txt"

# plt.plot([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
# plt.savefig('foo.png')
# plt.savefig('footight.png', bbox_inches='tight')


def load_jsonfile_arglists(filepath, *args, backwards = False, count = 0):
    """Function can help you to parse """
    output_lists = { arg: [] for arg in args }
    openfunc = open if backwards else FileReadBackwards
    with openfunc(filepath, encoding="UTF-8") as file:
        if not count:
            ## push all the values
            for line in file:
                parsed_line = json.loads(line)
                for arg in args:
                    output_lists[arg].append(parsed_line[arg])
        else:
            for index, line in enumerate(file, start=1):
                if index > count:
                    break
                parsed_line = json.loads(line)
                for arg in args:
                    output_lists[arg].append(parsed_line[arg])
    if not backwards:
        ## to restore original order -- list.append() puts new value to the end
        for values_list in output_lists.values():
            values_list.reverse()

    return [output_lists[arg] for arg in args]


def makeplot_datetime_interpolation(filename, values_timestamp, values_y, compress=300):
    """Compress arg changes interpolation. Requires numeric timestamps"""
    axes = plt.gca()
    axes.grid(True) # set grid
    axes.set_ylim([19.0, 30.0])

    lazy_intervals = {
        0: 5, # < 1 hour -- tick every 5 minutes
        1: 10, # < 2 hour -- tick every 10 minutes
        2: 20, # < 3 hour -- tick every 20 minutes
        3: 20, # < 3 hour -- tick every 20 minutes
        4: 30}    
    interval = lazy_intervals.get(int(len(values_timestamp) / (3*60)), 60) # calculate tick interval

    formfunc = lambda x,_: datetime.strftime(datetime.fromtimestamp(x), "%H:%M")
    formatter = matplotlib.ticker.FuncFormatter(formfunc)
    axes.xaxis.set_major_formatter(formatter)
    axes.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(base=interval*60))

    #compress -  represents number of points to make between T.min and T.max
    values_timestamp_new = np.linspace(min(values_timestamp),max(values_timestamp),compress) 
    spl = make_interp_spline(values_timestamp, values_y, k=3) #BSpline object
    values_y_smooth = spl(values_timestamp_new)

    plt.plot(values_timestamp_new,values_y_smooth)
    plt.savefig(filename+'.png')

def makeplot_datetime(filename, values_time, values_y):
    axes = plt.gca()
    axes.grid(True) # set grid
    axes.set_ylim([19.0, 30.0])

    lazy_intervals = {
        0: 5, # < 1 hour -- tick every 5 minutes
        1: 10, # < 2 hour -- tick every 10 minutes
        2: 20, # < 3 hour -- tick every 20 minutes
        3: 20, # < 3 hour -- tick every 20 minutes
        4: 30}
    
    interval = lazy_intervals.get(int(len(values_time) / (3*60)), 60) # calculate tick interval

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=interval))


    plt.plot(values_time, values_y)
    # plt.gcf().autofmt_xdate() # italic datetime
    plt.savefig(filename + '.png')

def filter_values(values, max_delta=0.5):
    deltas = [abs(values[x]-values[x+1]) for x in range(len(values)-1)] # without the last value

    if deltas[0] > max_delta and deltas[1] < max_delta: # error in the first item
        print(f'Error in [0] -- {values[0]}!, {values[1]}, {values[2]}')
        values[0] = values[1]
    if deltas[-1] > max_delta and deltas[-2] < max_delta: # error in the last
        print(f'Error in [-1] -- {values[-3]}, {values[-2]}, {values[-1]}!')
        values[-1] = values[-2]
    
    for _, delta in enumerate(deltas[1:], start=1):
        if delta > max_delta and deltas[_-1] > max_delta:
            print(f'Error in [{_}] -- {values[_-1]}, {values[_]}!, {values[_+1]}')
            values[_] = (values[_-1] + values[_+1]) / 2




if __name__ == "__main__":
    time, temp = load_jsonfile_arglists(log1, "timestamp", "temperature", backwards=True, count=3*60*4)
    filter_values(temp)

    time_dt = list(map(isoparse, time))
    time_dt2 = [isoparse(x).timestamp() for x in time]

    makeplot_datetime('bar', time_dt, temp)
    # makeplot_datetime2('bar20', time_dt2, temp, 20)