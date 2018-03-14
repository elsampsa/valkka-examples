from valkka.valkka_core import *

width  =1920//4
height =1080//4
cc     =3 # its rgb

shmem_name    ="lesson_4"      # This identifies posix shared memory - must be unique
shmem_bytes   =width*height*cc # Size for each element in the ringbuffer
shmem_buffers =10              # Size of the shmem ringbuffer

shmem=SharedMemRingBuffer(shmem_name, shmem_buffers, shmem_bytes, 1000 , False) # shmem id, buffers, bytes per buffer, timeout, False=this is a client
  
# pointers at the python side:
index_p =new_intp() # shmem index
isize_p =new_intp() # size of data
  
shmem_list=[]
for i in range(shmem_buffers):
  shmem_list.append(getNumpyShmem(shmem,i)) # getNumpyShmem defined in the swig interface file
  print("got element i=",i)
  
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
