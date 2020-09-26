import cv2
from valkka.api2 import ShmemRGBClient

width = 1920//4
height = 1080//4

# This identifies posix shared memory - must be same as in the server side
shmem_name = "lesson_4"
shmem_buffers = 10              # Size of the shmem ringbuffer

client = ShmemRGBClient(
    name=shmem_name,
    n_ringbuffer=shmem_buffers,
    width=width,
    height=height,
    mstimeout=1000,        # client timeouts if nothing has been received in 1000 milliseconds
    verbose=False
)

while True:
    index, meta = client.pullFrame()
    if (index == None):
        print("timeout")
        continue
    data = client.shmem_list[index][0:meta.size]
    print("data   : ", data[0:min(10, meta.size)])
    print("width  : ", meta.width)
    print("height : ", meta.height)
    print("slot   : ", meta.slot)
    print("time   : ", meta.mstimestamp)
    img = data.reshape((meta.height, meta.width, 3))
    # img2 =imutils.resize(img, width=500)
    img = cv2.GaussianBlur(img, (21, 21), 0)
    print("got frame", img.shape)
    ## depending on how you have installed your openCV, this might not work:
    ## (use at your own risk)
    #cv2.imshow("valkka_opencv_demo", img)
    #cv2.waitKey(1)
