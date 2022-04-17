import zmq
import zmq.asyncio


class Connector:
    """
    Data transmission class for performance monitor Client.
    """

    def __init__(self, host, port):
        self.context = zmq.asyncio.Context()
        self.host = host
        self.port = port
        self.sock = self.context.socket(zmq.PUB)
        self.sock.setsockopt(zmq.LINGER, 1)
        self.sock.connect(f'tcp://{host}:{port}')

    async def send_data(self, data):
        await self.sock.send_json(data)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print('Closing connection...')
        self.sock.close()
        self.context.term()
        print(f'Connection to {self.host}:{self.port} closed')

