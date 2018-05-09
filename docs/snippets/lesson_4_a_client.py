from valkka.valkka_core import *

width  =1920//4
height =1080//4

shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
shmem_buffers =10              # Size of the shmem ringbuffer

"""<rtf>
The wrapped cpp class is *SharedMemRingBufferRGB* (at the server side, RGBShmemFrameFilter is using SharedMemRingBufferRGB):
<rtf>"""
shmem=SharedMemRingBufferRGB(shmem_name, shmem_buffers, width, height, 1000, False) # shmem id, buffers, w, h, timeout, False=this is a client
  
"""<rtf>
We are using integer pointers from python:
<rtf>"""
index_p =new_intp() # shmem index
isize_p =new_intp() # size of data
  
"""<rtf>
Next, get handles to the shared memory as numpy arrays:
<rtf>"""
shmem_list=[]
for i in range(shmem_buffers):
  shmem_list.append(getNumpyShmem(shmem,i)) # getNumpyShmem defined in the swig interface file
  print("got element i=",i)
  
"""<rtf>
Finally, start reading frames:
<rtf>"""
while True:
  got=shmem.clientPull(index_p, isize_p)
  if (got):
    index=intp_value(index_p)
    isize=intp_value(isize_p)
    print("got index, size =", index, isize)
    ar=shmem_list[index][0:isize] # this is just a numpy array
    print("payload         =", ar[0:min(10,isize)])
  else:
    print("timeout")
