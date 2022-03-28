import zmq

context = zmq.Context()

receive = context.socket(zmq.SUB)
receive.setsockopt_string(zmq.SUBSCRIBE, '')
receive.bind('tcp://*:5555')

cmd_channel = context.socket(zmq.REQ)
cmd_channel.connect('tcp://127.0.0.1:5556')



while data := receive.recv_json():
    print(data)
    command = {
        'command': 'args'
    }
    req = cmd_channel.send_json(command)
    rep = cmd_channel.recv_json()
    print('Received: ', rep)