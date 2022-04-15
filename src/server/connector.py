import zmq
import zmq.asyncio


class Connector:
    """
    ZMQ connector.
    """

    def __init__(self, port=5555):
        self.port = port
        self.context = zmq.asyncio.Context()
        self.sock = self.context.socket(zmq.SUB)
        self.sock.setsockopt_string(zmq.SUBSCRIBE, '')
        self.sock.bind(f'tcp://*:{port}')

    async def receive_data(self):
        data = await self.sock.recv_json()
        return data

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print('Closing connection...')
        self.sock.close()
        self.context.term()
        print(f'Connection closed')
