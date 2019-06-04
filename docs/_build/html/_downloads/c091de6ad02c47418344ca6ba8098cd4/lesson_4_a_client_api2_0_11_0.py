"""<rtf>
This is a *separate* python program for reading the frames that are written by Valkka to the shared memory.

The parameters used both in the server side (above) and on the client side (below) **must be exactly the same** and the client program should be started *after* the server program (and while the server is running).  Otherwise undefined behaviour will occur.  

The used shmem_name(s) should be same in both server and client, but different for another server/client pair.
<rtf>"""
from valkka.api2 import ShmemRGBClient

width  =1920//4
height =1080//4

shmem_name    ="lesson_4"      # This identifies posix shared memory - must be same as in the server side
shmem_buffers =10              # Size of the shmem ringbuffer

client=ShmemRGBClient(
  name          =shmem_name, 
  n_ringbuffer  =shmem_buffers,   
  width         =width,
  height        =height,
  mstimeout     =1000,        # client timeouts if nothing has been received in 1000 milliseconds
  verbose       =False
)

"""<rtf>
The *mstimeout* defines the semaphore timeout in milliseconds, i.e. the time when the client returns even if no frame was received:
<rtf>"""
while True:
  index, isize = client.pull()
  if (index==None):
    print("timeout")
  else:
    data=client.shmem_list[index][0:isize]
    print("got data: ",data[0:min(10,isize)])

"""<rtf>
The *client.shmem_list* is a list of numpy arrays, while *isize* defines the extent of data in the array.  This example simply prints out the first ten bytes of the RGB image.
</rtf>"""
