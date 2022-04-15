import asyncio
import platform
import signal
from contextlib import suppress
from connector import Connector


# Костыль для ZMQ
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class PerfMonClient:
    """
    Gather and send metrics to Server.
    """

    def __init__(self, host='127.0.0.1', port='5555', interval=5):
        self.host = host
        self.port = port
        self.interval = interval
        self.metrics = {}
        self.tasks = []
        self.node = platform.node()
        signal.signal(signal.SIGINT, self.shutdown)

    def run(self):
        asyncio.run(self.serve())

    async def serve(self):
        t1 = asyncio.create_task(self.collector(), name='collector_coro')
        t2 = asyncio.create_task(self.interrupt_loop(), name='interruptor')
        self.tasks.append(t1)
        self.tasks.append(t2)
        with suppress(asyncio.CancelledError):
            await t1
            await t2

    async def collector(self):
        async with Connector(self.host, self.port) as conn:
            while True:
                data = self.collect()
                response = {
                    'node': self.node,
                    'measurements': data,
                }
                await conn.send_data(response)
                await asyncio.sleep(self.interval)

    async def interrupt_loop(self):
        while True:
            await asyncio.sleep(0.1)

    def collect(self):
        try:
            return {metric_name: metric_collector() for metric_name, metric_collector in self.metrics.items()}
        except Exception as err:
            print('Error', err)

    def add_metric(self, metric_name, metric_collector):
        self.metrics[metric_name] = metric_collector

    def del_metric(self, metric_name):
        del self.metrics[metric_name]

    def all_metrics(self):
        return list(self.metrics.keys)

    def set_interval(self, interval):
        self.interval = int(interval)
        return f'{self.node} interval set to {interval}'

    def shutdown(self, *args):
        print('Shutting down client...')
        for task in self.tasks:
            task.cancel()


if __name__ == '__main__':
    from metrics import cpu_percent, ram_percent
    c1 = PerfMonClient(interval=2)
    c1.add_metric('CPU', cpu_percent)
    c1.add_metric('RAM', ram_percent)
    c1.run()
