import asyncio
import platform
import signal
from importlib import import_module
from connector import Connector


# Костыли для ZMQ и обработки сигналов
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# signal.signal(signal.SIGINT, signal.SIG_DFL)


METRIC_MODULE = 'metrics'


class Client:
    """
    Gather and send metrics to Server.
    """

    def __init__(self, connector, delay=5):
        self.connector = connector
        self.delay = delay
        self.metrics = {}
        self.node = platform.node()
        self.architecture = platform.architecture()[0]
        signal.signal(signal.SIGINT, self.destroy)

    def run(self):
        asyncio.run(self.serve())

    async def serve(self):
        t1 = asyncio.create_task(self.collector_coro())
        t2 = asyncio.create_task(self.cmd_listen_coro())
        await asyncio.gather(t1, t2, return_exceptions=True)

    async def collector_coro(self):
        while True:
            data = self.gather()
            data['node'] = self.node
            data['architecture'] = self.architecture
            await self.connector.send_data(data)
            await asyncio.sleep(self.delay)

    async def cmd_listen_coro(self):
        while True:
            cmd = await self.connector.listen_for_command()
            print(cmd)

    def gather(self):
        try:
            return {metric_name: func() for metric_name, func in self.metrics.items()}
        except Exception as err:
            print(err)

    def add_metric(self, metric_name):
        metric_collector = self.import_metric_collector(metric_name)
        if metric_collector is not None:
            self.metrics[metric_name] = metric_collector

    def del_metric(self, metric_name):
        try:
            del self.metrics[metric_name]
        except KeyError:
            print('No such metric in observation')

    def run_command(self):
        pass

    def load_cfg(self):
        pass

    def save_cfg(self):
        pass

    def destroy(self, *args):
        print('Shutting down client...')
        for task in asyncio.all_tasks():
            print(task)
            task.cancel()
        loop = asyncio.get_running_loop()
        loop.close()



    @staticmethod
    def import_metric_collector(metric_name):
        metric_collector = None
        mod = import_module(METRIC_MODULE)
        try:
            metric_collector = getattr(mod, metric_name)
        except KeyError:
            print('No such metric collector.')
        finally:
            return metric_collector

    def __str__(self):
        return f'{self.node}, {self.architecture}'


if __name__ == '__main__':
    conn = Connector()
    c1 = Client(conn, delay=1)
    print(c1)
    c1.add_metric('cpu_percent')
    c1.run()
