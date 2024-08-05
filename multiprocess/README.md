## Valkka multiprocessing examples

Here you find small python example programs where we receive RGB (bitmap) frames from IP cameras and then
share those frames with python multiprocesses.

These multiprocesses can do whatever they please with the frames: save them to disk, analyze them, send analysis results downstream, etc.

A few different frame-sharing/multiprocessing topologies are considered.

## Prerequisites

- [Python multiprocessing](https://docs.python.org/3/library/multiprocessing.html) and [valkka multiprocessing](https://elsampsa.github.io/valkka-multiprocess/_build/html/index.html)
- [select module](https://docs.python.org/3/library/select.html), unix file descriptors (fds) and blocking vs. non-blocking fd reading (see, say, the [socket tutorial](https://docs.python.org/3/howto/sockets.html))
- [Valkka tutorial](https://elsampsa.github.io/valkka-examples/_build/html/tutorial.html)

## Under-the-hood

POSIX shared memory, semaphore synchronization, C++, multiplexing file descriptors, etc.  But *you* don't need to worry about any of that - just use the python API.

## What's in the files?
```
main1.py        Send stream from N cameras to a single client multiprocess
main2.py        Send stream from N cameras to N client multiprocesses
                (i.e. each camera has it's own client multiprocess)
main3.py        Like main2.py, but each client multiprocess additionally communicates
                downstream with a common "master" process that sends some results upstream
rgb.py          Multiprocessing class for main1.py and main2.py
client.py       multiprocessing class for main3.py
master.py       master process class for main3.py
singleton.py    global module for creating and sharing synchronization primitives
```

Program `main3.py` is for situations where a client process does some "light" analysis and/or heuristics and say, for example, database operations
as per camera, while all client processes share a single common "heavy" analyzer, say, a torch-based neural net analyzer, etc. (think of yolo, etc.)

## Danger Zone

Multiprocessing and threading applications are inherently complex and prone to nasty and hard-to-debug errors.

Here we have gone through most of the nasty program organization stuff, so that *you* can concentrate on building your application instead. :)

However, remember to read all code comments carefully and keep in mind that:

*1. All synchronization primitives (events, pipes, etc.) must be started before forking multiprocesses*

This is the way they become visible to all multiprocesses.

*2. All threads must be started before multiprocesses*

Otherwise strange crashes will occur.  A basic truth of multiprocessing.

*3. An shmem server must be started before the corresponding shmem client*

If you see corrupt rgb frames and weird crashes, this is the likely culprit.

*4. Information sent from the main python process (aka frontend) to a multiprocess (aka backend) can only be simple types*

For the simple reason that messages to the multiprocess are serialized using pickle.  For this reason we communicate synchronization primitive indexes of pre-reserved event objects, instead of the event objects themselves (see the code for more details)

*5. Remember to clear shared-memory related objects.  First the client and then the server.*

Otherwise your `/dev/shm` directly slowly saturates with files occupying loads of your ram memory each time you restart the program.  Always first clear/garbage collect the shmem client and after that the server.  See the code for more details.

*6. Clean manually dirty exits*

If your program crashes, remember to
```
killall -9 python3
rm -f /dev/shm/*valkka*
```

*7. Don't skip the essentials*

You **must** read carefully the valkka multiprocessing documentation and the associated article therein (see above) in order to understand *any* of this.  Trust me on this one.

## Code at a glance

All example codes follow this scheme:
```
main python process
    - creates RGB frame shmem server (see class LiveStream)
    - instantiates MasterProcesses, RGB24Processes and ClientProcesses

    MessageProcess (from valkka.multiprocess)
        - general multiprocessing base class
        - see valkka multiprocess docs for more details
        
    RGB24Process (rgb.py) / subclass of MessageProcess
        - receives RGB frames and does something with them
        methods:
            activateRGB24Client
                - creates RGB frame shmem client that
                  connects to the main python process' 
                  RGB frame shmem server (see above)
            deactivateRGB24Client (from RGB24Process)
                - removes RGB frame shmem client
    
    ClientProcess (client.py) / subclass of RGB24Process
        - receives RGB frames, analyzes them and forwards 
          them to a MasterProcess
        - creates shmem data client to
          receive replies from a MasterProcess
        - creates internal RGB frame shmem server 
          (to be used by a MasterProcess)
        - creates internal data shmem server 
          (to be used by other downstream processes)
        methods:
            getRGB24ServerPars
                - returns parameters of the internal 
                  RBG frame shmem server for client creation
            getDataShmemPars
                - returns parameters of the internal 
                  data shmem server for client creation
            listenDataServer
                - starts listening to a data server 
                  (typically to MasterProcess)
            dropDataServer
                - stops listening to a data server

    MasterProcess (master.py) / subclass of MessageProcess
        - gets RBG frames from ClientProcesses and replies to them 
          with a message
        methods:
            registerClientProcess(p: ClientProcess)
                - starts listening to ClienProcesses' internal 
                  RGB frame shmem server: uses ClientProcess.getRGB24ServerPars
                - creates an shmem data server for ClientProcess 
                  to listen
                - tells ClientProcess to listen to the newly 
                  created data server: uses ClientProcess.listenDataServer
            deregisterClientProcess(p: ClientProcess)
                - ditto    
```
