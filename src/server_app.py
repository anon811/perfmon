from server import PerfMonServer
from server.data_processors import Plotter


if __name__ == '__main__':
    pm_server = PerfMonServer()
    plt = Plotter()
    pm_server.add_data_processor(plt)
    pm_server.run()
