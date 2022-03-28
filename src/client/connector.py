import asyncio
import zmq, zmq.asyncio


class Connector:
    """
    Data transmission class
    """

    def __init__(self, host='127.0.0.1', port=5555, cmd_port=5556):
        self.context = zmq.asyncio.Context()
        self.init_connections(host, port, cmd_port)

    def init_connections(self, host, port, cmd_port):
        self.sender = self.context.socket(zmq.PUB)
        self.sender.setsockopt(zmq.LINGER, 1)
        self.sender.connect(f'tcp://{host}:{port}')
        self.cmd_reciever = self.context.socket(zmq.REP)
        self.cmd_reciever.bind(f'tcp://*:{cmd_port}')

    async def send_data(self, data):
        loop = asyncio.get_running_loop()
        await self.sender.send_json(data)
        # await loop.run_in_executor(None, self.sender.send_json, data)

    async def listen_for_command(self):
        loop = asyncio.get_running_loop()
        command = await self.cmd_reciever.recv_json()
        # command = await loop.run_in_executor(None, self.cmd_reciever.recv_json)
        rep = {
            'result': 'ok'
        }
        await self.cmd_reciever.send_json(rep)
        # await loop.run_in_executor(None, self.cmd_reciever.send_json, rep)
        return command