"""A poor man's cookiecutter for the tutorial.  Creates a copy of all tutorial code and substitutes the original rtsp directions with custom ones
"""

import os
import glob

subs={}

# if you need to change the camera ip adresses of the tutorial, enable this:
"""
subs={
  "rtsp://admin:nordic12345@192.168.1.41" : "rtsp://admin:12345@192.168.0.157", # first camera used in the tutorial and its substitution
  "rtsp://admin:nordic12345@192.168.1.42" : "rtsp://admin:12345@192.168.0.157"  # second camera used in the tutorial and its substitution
  }
"""

os.system("mkdir tmp")
os.system("cp -f api_level_1/tutorial/* tmp/")
os.system("cp -f api_level_2/tutorial/* tmp/")
os.system("cp -f aux/run_tutorial.bash tmp/")
os.system("cp -f aux/run_tutorial_shmem.bash tmp/")

lis=glob.glob("tmp/*.py")
for l in lis:
  print(l)
  f=open(l,"r")
  st=f.read()
  f.close()
  for key in subs:
    st=st.replace(key,subs[key])
  f=open(l,"w")
  f.write(st)
  f.close()

