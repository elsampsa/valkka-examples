from valkka.core import *

width = 1920//4
height = 1080//4

shmem_name = "lesson_4"  # This identifies posix shared memory - must be unique
shmem_buffers = 10       # Size of the shmem ringbuffer

"""<rtf>
The wrapped cpp class is *SharedMemRingBufferRGB* (at the server side, RGBShmemFrameFilter is using SharedMemRingBufferRGB):
<rtf>"""
shmem = SharedMemRingBufferRGB(shmem_name, shmem_buffers, width, height,
                               1000, False)  # shmem id, buffers, w, h, timeout, False=this is a client

"""<rtf>
Next, get handles to the shared memory as numpy arrays:
<rtf>"""
shmem_list = []
for i in range(shmem_buffers):
    # getNumpyShmem defined in the swig interface file
    shmem_list.append(getNumpyShmem(shmem, i))
    print("got element i=", i)

"""<rtf>
Finally, start reading frames.

shmem.clientPullPy() returns a tuple with the shared memory ringbuffer
index and metadata.

<rtf>"""
while True:
    tup = shmem.clientPullPy()
    index = tup[0]
    if index < 0:
        print("timeout")
        continue
    isize         = tup[1]
    width         = tup[2]
    height        = tup[3]
    slot          = tup[4]
    mstimestamp   = tup[5]
    print("got index, size =", index, isize)
    ar = shmem_list[index][0:isize]  # this is just a numpy array
    ar = ar.reshape((height, width, 3)) # this is your rgb image
    print("payload         =", ar.shape)
