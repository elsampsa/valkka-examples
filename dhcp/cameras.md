## Network interfaces
 
Create two interfaces for the planet switch:

1. "planet switch"

This is for normal use

restrict to: enps0[ETC]

adr: 10.0.0.1
netmask: 255.0.0.0
gw: 0.0.0.0


2. "planet switch default"

Use this to connect to the switch after a reset

restict to: enps0[ETC]

adr: 192.168.0.33
netmask: 255.255.255.0
gw: 192.168.0.100


## DHCP

```
apt -y install isc-dhcp-server 
sudo systemctl stop isc-dhcp-server
sudo systemctl disable isc-dhcp-server
```

in the case of problems:
```
ps ax | grep dhcpd
sudo killall dhcpd
```

Edit this file:

/etc/dhcp/dhcpd.conf

to have these lines:

default-lease-time 99999;
max-lease-time 99999;

subnet 10.0.0.0 netmask 255.0.0.0 {
 range 10.0.0.2 10.0.0.255;
 option routers 10.0.0.1;
 option domain-name-servers 10.0.0.1;
 option domain-name "mydomain.example";
}


Start dhcp server interactive like this:

```
sudo dhcpd -f
```

Activate interface "planet switch default" and check where your devices are 
with "sudo arp-scan --localnet --interface enp0s31f6" and you're ready to go!


## Credentials

#### Planet switch password

admin

#### Axis

root / silopassword

rtsp://root:silopassword@ip-address/axis-media/media.amp

rtsp://root:silopassword@10.0.0.2/axis-media/media.amp

rtsp://admin:123456@10.0.0.4

rtsp://admin:nordic12345@10.0.0.5


#### Scheme

1. start router
2. plug-in eth cable (interface "planet switch" activates automatically)
3. start dhcp.bash
4. start findsome.bash

Planet switch should be visible at: http://10.0.0.3
(remember: _not_ httpS)







