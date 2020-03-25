# Hosting with `seabreeze-server`
In this example, we will walk through the steps to setup an emulated 
`SeaBreezeServer` object on Amazon Web Service's Elastic Cloud 2. This will
illustrate 


## Setting up `EC2`
Register for a (or log into your) AWS account, and start a new EC2 instance.
You want an ubuntu server (there are tons of tutorials on this, look one up...).
Once it is running, you will need 2 things:

1) The server's static IP address (visible on the `Instances` page)

2) Change the `Security Groups` to allow TCP connections.

For this, from the `Instances` page, click on the security group link for
your server (probably: 'launch-wizard-1', or something like that). From there
click on `Inbound rules` -> `Edit inbound rules` -> `Add rule`. You want to
make the type `Custom TCP`, the port range `8001` and the source `0.0.0.0/0`. 
Then click `Save rules`.

Essentially, you have told `EC2` that if someone tries to make a TCP request
to your sever on the external port `8001`, let them do that. If you skip this
step, your `EC2` will reject all TCP request, and your server will never see
them. (This is analogous to port forwarding, if you are familiar with that)  

## Base installations
After getting the ubuntu server running, ssh into it (instructions under `Connect`
on the `Instances` page) and start installing the 
dependancies:
```bash
 $ sudo apt-get update
 $ sudo apt-get install python3-pip
 $ sudo apt-get install python3-venv
 $ sudo apt-get install git
 $ sudo apt-get install nginx
```

## Configure `nginx`
`nginx` is a reverse proxy webserver. Basically, it sits at the interface of
your server's internal TCP ports (how your server talks to itself) and your
server's external TCP ports (how other computers talk to your server). What 
`nginx` does is it listens on the external ports and when a request comes in
from another computer, it has a protocol to forward that request to an internal
port, and then return any values back.

So, we will be hosting the `SeaBreezeServer` object on the internal TCP port 
`8002` (that is, it is accessable only internally to the server at `localhost:8002`),
then we will configure `nginx` to forward any external requests coming into
the external port `8001` to forward to the internal port `8002`.

Why are we doing this? Well, using the reverse proxy has the advantage that if
your server wants to do anything with the `SeaBreezeServer` has has internal
access to it, rather than having to use the external port. This is important
if you want to, say, run a parallel web application on the same server, which
can provide a graphic user interface to users (a la `spectra-sweet`), while
still allowing direct TCP control of the spectrometer.

To setup `nginx` to forward inbound TCP requests  to the local TCP
port where `seabreeze-server` will be hosting, open up the `/etc/nginx/nginx.conf`
file and append the following:
```bash
 $ sudo vim /etc/nginx/nginx.conf
```
```
# ...

stream {
    server {
        listen 8001; # listen for external request
        forward_proxy 127.0.0.1:8002; # forward to localhost:8002
    }
}

# ...

```
Then, check for syntax errors and restart `nginx`:
```bash
 $ sudo nginx -t
 $ sudo systemctl restart nginx
```

## Hosting the server
Next, clone this directory onto your server, create a virtual python environment
and run the server:
```bash
 $ git clone https://github.com/jonathanvanschenck/python-seabreeze-server.git
 $ cd python-seabreeze-server/example
 $ python3 -m venv venv
 $ source venv/bin/activate
 (venv) $ pip install -r requirements.txt
 (venv) $ python server.py
 
Hosting @ ('127.0.0.1', 8002)

```

## Connecting to the server
If all goes well, from your own computer, you should be able to connect. In
a python shell (running, well, anywhere):
```python
 >>> import seabreeze_server as sbs
 >>> c = sbs.client.SeaBreezeClient("server's ip address here", 8001)
 >>> c
<Remote Wrapper <Spectrometer Manager : 1 devices: Current: None>>
```
if instead you get something like:
```python
<Remote Wrapper pointed at ip_address_here:8001>
```
it means your client couldn't find the server, and you did something wrong...