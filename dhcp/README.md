## Test camera studio

How to manage a collection of IP cameras connected to your laptop via a switch - nice for testing and development!


First install the dhcpd server and arp-scan with:
```
sudo apt install isc-dhcp-server arp-scan
```
Check & disable any competing dhcp servers:
```
sudo systemctl status udhcpd
```
Check that dhcpd is not running as a daemon:
```
sudo systemctl status dhcpd
```

### Hardware

You need:

- A Power on Ethernet (PoE) switch
- Several IP cameras (preferably with diverse brands and models)

Connect all your IP (PoE) cameras to the (PoE) network switch

### Config

Create a dedicated wired connection in your network manager:

- Use "restrict to device" to restrict the new wired connection to your PoE switch only

- Use the following confguration for the device:
  ```
  Manual IPv4 configuration
  DNS Servers: 0.0.0.0
  Address: 10.0.0.1
  Netmask: 255.0.0.0
  Gateway: 0.0.0.0
  ```

### Run

Start [dhcp.bash](dhcp.bash) and keep it running - now your have a dhcp server that serves the cameras connected to the PoE switch

Edit and run [findsome.bash](findsome.bash) - this discovers the IP addresses of the cameras connected to the PoE switch

You can also edit [dhcpd.conf](dhcpd.conf) for setting fixed IP addresses for your cameras (after this you need to restart ``dhcp.bash``).

