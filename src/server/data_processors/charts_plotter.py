import multiprocessing as mp
import matplotlib.pyplot as plt
from contextlib import suppress
from collections import defaultdict, deque
from queue import Empty


AXIS_LENGTH = 1000


class ProcessPlotter:
    """
    Plots graphs from the received data.
    """

    def __init__(self, q, window_title=None):
        self.q = q
        self.window_title = window_title
        self.charts = defaultdict(self.init_data_storage)

    def __call__(self, *args, **kwargs):
        with suppress(KeyboardInterrupt):
            self.fig, self.ax = plt.subplots()
            if self.window_title and isinstance(self.window_title, str):
                self.fig.canvas.set_window_title(self.window_title)
            self.ax.get_xaxis().set_visible(False)
            timer = self.fig.canvas.new_timer(interval=1000)
            timer.add_callback(self.call_back)
            timer.start()
            plt.show()

    def update_charts(self):
        with suppress(KeyboardInterrupt):
            try:
                data = self.q.get_nowait()
            except Empty:
                return
            for k, v in data.items():
                self.charts[k].popleft()
                self.charts[k].append(v)

    def draw(self):
        self.ax.cla()
        for title, data in self.charts.items():
            self.ax.plot(data)
            self.ax.scatter(len(data)-1, data[-1])
            self.ax.text(len(data)-1, data[-1]+2, f'{title}: {data[-1]}%')
            self.ax.set_ylim(0, 100)
        self.fig.canvas.draw()

    def call_back(self):
        with suppress(KeyboardInterrupt):
            self.update_charts()
            self.draw()

    @staticmethod
    def init_data_storage():
        return deque(0.0 for i in range(AXIS_LENGTH))


class Plotter:
    """
    Spawns a chart plotter process for each node connection.
    """

    def __init__(self):
        self.nodes = defaultdict(mp.Queue)
        self.plot_processes = []

    def __call__(self, data):
        node = data['node']

        if node not in self.nodes:
            q = self.nodes[node]
            self.spawn_node_plotter(q, node)

        self.nodes[node].put(data['measurements'])

    def spawn_node_plotter(self, q, window_title):
        plotter = ProcessPlotter(q, window_title=window_title)
        plot_process = mp.Process(target=plotter)
        self.plot_processes.append(plot_process)
        plot_process.start()

    def stop(self):
        print('Stopping plotter...')
        [proc.terminate() for proc in self.plot_processes]
        [proc.join() for proc in self.plot_processes]

