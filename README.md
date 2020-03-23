# Seabreeze-Server
A python TCP-Server which allows a OceanOptics Spectrometer to be connected to 
over a network

The purpose of this library is to allow OceanOptics spectrometers to be
effectively wifi-enabled, so that data-aquisition can be handled by multiple
computers (some potentially offsite), without having to fiddle with usb cords.
Additionally, this opens up the possibility for open-source, web-based user 
interfaces to be developed for OceanOptics devices.

This package uses the `seabreeze.cseabreeze` backend to handle communications
between the server and the spectrometer, by exposing the backend API functions
to the `seabreeze_server.server.SpectrometerManager` object. (Alternatively,
a physical spectrometer can also be emulated in software with the 
`seatease` package, but setting `SpectrometerManager(emulate=True)`). The TCP
server is handled by the `seabreeze_server.server.SeaBreezeServer` class 
(based on the `remote-object` package), which exposes the `SpectrometerManager` 
object's methods and attributes to `seabreeze_server.client.SeaBreezeClient`
instances.

# Basic Use
On the server-side, connect and configure your spectrometer hardware for
whatever kind of measurement you desire, then run something like:
```python
HOST, PORT = 'your-ip', 9999
with seabreeze_server.server.SeaBreezeServer(
    (HOST, PORT),
    emulate = False
) as server:
    server.serve_forever()
```
See the `socketserver.TCPServer` documentation for more ideas about
how to manage this server.

Then on the client-side, run something like the following:
```python
HOST, PORT = 'your-ip', 9999
client = seabreeze_server.client.Client(HOST, PORT)

# Prints out currently plugged-in devices
print(
    "Available Devices:\n",
    "\n".join(["%d : %s" % (i,dev)\
                for i,dev in enumerate(client.list_devices())
             ])
)

# Select the first spectrometer
client.select_spectrometer(0)

# Set integration time to 10 ms
client.set_integration_time_micros(10*1000)

# Get wavelengths and intensities
wls = client.get_wavelengths()
i = client.get_intensities()
```

# Installing (`pip`)
`seabreeze-server` is available via pip:
```bash
 $ pip install seabreeze-server
```
If you haven't previously installed `seabreeze`, you might need to do a bit of
work, see 'SeaBreeze Setup' below for more details. 

# SeaBreeze Setup
Installing `seabreeze` can take some trial an error, especially on linux,
make sure that after `pip` installing (or `conda` installing, whatever, 
you do you) you are also run the os setup script:
```bash
 $ pip install seabreeze
 $ seabreeze_os_setup
```
If you are still having trouble, check out the main `seabreeze` documentation.

# Development
For development, clone this directory, then have fun! Pro-tip: setup a python
virtual environment in the main directory:
```bash
 $ python3 -m venv venv
 $ source venv/bin/activate
```
## Installing
```bash
 (venv) $ python3 setup.py install
 (venv) $ seabreeze_os_setup
```

## Creating source packages
```bash
 (venv) $ python3 setup.py sdist bdist_wheel 
```

## Uploading to PyPI
```bash
 (venv) $ python3 -m twine upload dist/*
```

See: [https://packaging.python.org/tutorials/packaging-projects/]

# Acknowledgements
The authors would like to thank [Andreas Poehlmann](https://github.com/ap--) 
and collaborators for creating the original `python-seabreeze` package, 
which this library depends heavily upon. His package has been indispensable 
to our research.