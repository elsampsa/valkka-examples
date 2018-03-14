from valkka.api2.threads import ShmemClient

width  =1920//4
height =1080//4
cc     =3 # its rgb

shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
shmem_bytes   =width*height*cc # Size for each element in the ringbuffer
shmem_buffers =10              # Size of the shmem ringbuffer

client=ShmemClient(
  name          =shmem_name, 
  n_ringbuffer  =shmem_buffers,   
  n_bytes       =shmem_bytes,    
  mstimeout     =1000,        # client timeouts if nothing has been received in 1000 milliseconds
  verbose       =False
)

while True:
  index, isize = client.pull()
  if (index==None):
    print("timeout")
  else:
    data=client.shmem_list[index][0:isize]
    print("got data: ",data[0:min(10,isize)])

