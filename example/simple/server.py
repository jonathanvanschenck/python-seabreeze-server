import seabreeze_server as sbs

HOST, PORT = 'localhost', 2999

with sbs.server.SeaBreezeServer((HOST, PORT), emulate=True) as server:
    print("Hosting @",server.server_address)
    server.serve_forever()
