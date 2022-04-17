from client import PerfMonClient
from client.collectors import psutil_collectors


if __name__ == '__main__':
    pm_client = PerfMonClient(interval=2)
    pm_client.add_metric('CPU', psutil_collectors.cpu_percent)
    pm_client.add_metric('RAM', psutil_collectors.ram_percent)
    pm_client.run()



