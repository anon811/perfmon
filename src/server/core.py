import asyncio
import signal
from contextlib import suppress
from .connector import Connector


# Костыль для ZMQ
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class PerfMonServer:
    """
    Server for remote performance monitoring.

    To start server use `run` method.
    After the launch starts listening to the port specified in the "port" parameter.
    The received data is processed using data processors. To add data processor
    use `add_data_processor` method.
    """

    def __init__(self, port=5555):
        self.port = port
        self.tasks = []
        self.data_processors = set()
        signal.signal(signal.SIGINT, self.shutdown)

    def run(self):
        asyncio.run(self.serve())

    def add_data_processor(self, processor):
        self.data_processors.add(processor)

    async def serve(self):
        t1 = asyncio.create_task(self.collector())
        t2 = asyncio.create_task(self.interrupt())
        self.tasks.append(t1)
        self.tasks.append(t2)
        with suppress(asyncio.CancelledError):
            await t1
            await t2

    async def collector(self):
        async with Connector(port=self.port) as conn:
            while data := await conn.receive_data():
                for processor in self.data_processors:
                    processor(data)

    async def interrupt(self):
        while True:
            await asyncio.sleep(0.1)

    def shutdown(self, *args):
        print('Server is shutting down...')
        for data_processor in self.data_processors:
            data_processor.stop()
        for task in self.tasks:
            task.cancel()
