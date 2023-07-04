"""Finds cameras in your LAN and produces yaml format that can be used as an input to the
rtsp_fps_test.py program

Run this program with the --help switch to get more info
"""
from pathlib import Path
import argparse, sys
from valkka.discovery import runWSDiscovery, runARPScan

def process_cl_args():
    comname = Path(sys.argv[0]).stem
    parser = argparse.ArgumentParser(
        usage=(
            f'{comname} [options]\n'
            '\n'
            'Searches cameras and produces yaml output for rtsp_fps_test.py\n'
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--arp", action="store_true", help="Use additional ARP scan", 
        default=False)
    parser.add_argument("--out", action="store", default="out.yaml", help="output file", type=str)
    parsed, unparsed = parser.parse_known_args()
    for arg in unparsed:
        print("Unknow option", arg)
        sys.exit(2)
    return parsed

p = process_cl_args()
ips = runWSDiscovery()
# print(ips)
ips2 = []
if p.arp:
    ips2 = runARPScan(exclude_list = ips)
ips = ips + ips2

"""Let's produce the following format:

::

    streams:
        - name: that camera
          address: rtsp://user:passwd@192.168.1.12
        - name: that other camera
          address: rtsp://user:passwd@192.168.1.13
"""
st = "streams:\n"
for i, ip in enumerate(ips):
    st += (
        f"    - name: camera-{i}\n"
        f"      address: rtsp://admin:12345@{ip}\n"
    )
with open(p.out, "w") as f:
    f.write(st)
print("Wrote", p.out)
print("If cams are missing, you might want to try arp scan with option --arp")
print("Have a nice day!")


