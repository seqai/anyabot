import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

class ChartService(object):
    def __init__(self):
        plt.cla()
    
    def plot_pie(self, data, output):
        labels = data["labels"]
        sizes = data["values"]

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.savefig(output, format="png")
        plt.cla()

    def plot_bars(self, data, output):
        ind = np.arange(len(data["x"]))    # the x locations for the groups
        width = 0.6       # the width of the bars: can also be len(x) sequence
        bars = []

        offset = [0 for n in ind]
        for dataset in data["values"]:
            bar = plt.bar(ind, dataset, width, bottom=offset)
            bars.append(bar[0])
            offset = [x + y for x, y in zip(offset, dataset)]

        plt.xticks(ind, data["x"])
        # plt.yticks(np.arange(0, 81, 10))
        plt.legend(bars, data["labels"])
        plt.savefig(output, format="png")
        
        plt.cla()

