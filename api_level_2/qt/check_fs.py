from valkka.api2 import ValkkaFS
fs = ValkkaFS.loadFromDirectory("fs_directory")
fs.analyzer.dumpBlock(1)

