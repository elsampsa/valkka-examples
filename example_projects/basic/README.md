 
# An Example Valkka Multiprocessing Project

*prerequisites*

- Subclassing [python multiprocesses](https://docs.python.org/3.6/library/multiprocessing.html#the-process-class)
- Understanding what "select" is about, see for example [here](https://docs.python.org/3/howto/sockets.html)
- [libValkka tutorial](https://elsampsa.github.io/valkka-examples/_build/html/tutorial.html)
- Asynchronous python

Trying to manage large video streaming / machine vision systems requires you to joggle
video streams between various threads and/or processes (regardless of your programming language of choice)
and will always, and without exceptions, create an impenetrable mess.

[This talk](https://drive.google.com/file/d/19VXmhTYi19EKDlSorv-Tmd0gholeD9SJ/) gives you some typical example cases you might and will run into.
This example repo also gives you code that can be used to resolve those example cases.

LibValkka comes to your help: you can write clean python code, where different parts of your system run in isolated
python multiprocesses.  Within the isolated multiprocesses you are free to use neural nets and OpenCV as you wish.
You can also create a websocket server, running asyncio python and serving frag-mp4 streams.

So, no more encapsulating those ffmpeg processes into separate multiprocesses and reading their stdout and things like that.  How cools is that!?

LibValkka uses python multiprocessing (*not* multi*threading*) and shared memory to pass video streams (and other data) between processes.
One process can also "multiplex" several streams simultaneously, either using asyncio python or python's select module.
[Eventfd](https://linux.die.net/man/2/eventfd) is heavily used.

This is all very neat, but of course, comes with a price tag in the form of a learning curve.  However, it's much better than paper-clip & house-of-cards solutions and besides, so much more enjoyable..!

Here we have a complete example of a multiprocess orchestration, which you can install with (launch in this directory):
```
pip3 install --user -e.
```

Remember also to install libValkka (as instructed [here](https://elsampsa.github.io/valkka-examples/_build/html/index.html)).

After that, you can move into ``skeleton/`` directory and launch ``python3 main.py rtsp://username:passwd@ip``

This example project can be used to create a websocket-based IP-camera stream server that does simultaneous machine vision analysis with OpenCV.  It is easily scaled up to a massive number of IP cameras.

Here are some details about the project structure:
```
.
├── basic
│   ├── figs
│   ├── setup.py
│   └── skeleton
│       ├── cli.py
│       ├── constant.py
│       ├── data
│       ├── demo
│       ├── filterchain
│       │   ├── basic.py            # your libValkka filterchain running in c++ side is defined here
│       │   └── __init__.py
│       ├── __init__.py
│       ├── local.py
│       ├── main.py                 # main process: edit this file's main() method
│       ├── multiprocess            
│       │   ├── client.py           # reads RGB24 frames from libValkka c++ side & passes them to master.py
│       │   ├── fragmp4.py          # reads fragmp4 from libValkka c++ side
│       │   ├── __init__.py
│       │   ├── master.py           # get's RGB24 frames from client.py & replies to client.py with a message
│       │   └── rgb.py              # reads RGB24 frames from libValkka c++ side
│       ├── singleton.py            # global inter-process communication objects
│       ├── template.py
│       ├── tools.py
│       └── version.py
└── README.md                       # this file
```


The code itself servers as a tutorial, and we suggest that you proceed like this:

- Read ``singleton.py``
- Read ``basic.py``
- Study method ``main1`` in ``main.py`` & proceed to ``rgb.py`` and ``fragmp4.py``
- Study method ``main2`` in ``main.py`` & proceed to ``client.py`` and ``master.py``

# Concepts

## The frontend/backend model of multiprocessing

*not to be confused with web front/backends, of course*

Here is a nice way to extend [python's multiprocessing class](https://docs.python.org/2/library/multiprocessing.html#the-process-class):

```
                          pipe
                          intercom
backend                  <--------->  frontend 

                                      def __init__(self)
def c__someCommand(pars)              def someCommand(pars)
def run                               def start(self)
...                                   ...

```

"backend" corresponds to the (forked) multiprocess running in its own, isolated virtual memory space.  The multiprocess (and backend) is created, once you
call your multiprocess classes' ``start`` method.

"frontend" methods can be called in the context/frame of your python main process

We have created more advanced subclasses from the [python multiprocessing class](https://docs.python.org/2/library/multiprocessing.html#the-process-class):

Namely, when you call ``someprocess.someCommand(pars)`` in the frontend, the parameters are silently communicated to the backend and
the corresponding ``c__someCommand(pars)`` is executed therein.

Backend may also run asynchronous python.

To learn more about this, please take a look at the files under the ``multiprocess`` folder.

Multiprocess orchestration/control examples can be found in the file ``main.py``.

## Shared memory servers and clients

You typically instantiate a shared memory server at the libValkka c++ side and within your main python process.  The shared memory client (to receive for example RGB24 frames) is typically instantiated at your multiprocesses' backend.

You can also instantiate a server in the multiprocess backend (to distribute those RGB24 frames further to other processes).

The complication that arises from this approach is, that the shared memory servers and clients need to intercommunicate the shared memory segment names and other information - but
they live in different multiprocesses.  Luckily, the frontend/backend model of multiprocessing we just discussed, makes things much easier.  Please refer to the ``multiprocess`` folder
to see how this is dealt with.

## Global inter-process communication variables

As already discussed, global event file descriptors are created in the very beginning of your program in the ``singleton.py`` module.

After that, ``singleton.events`` are visible to all of your python code.  They are also visible to any multiprocess (backends) you might span later on in your program.

Regularly, your main python process needs to tell to a multiprocess (backend), which eventfd it should use to synchronize a stream of RGB24 frames, originating from the main python process.

The main process must send this information as a global index, referring to an element in ``singleton.events``.

*The indices (and eventfds) should only be reserved / released by the main python process* (see ``singleton.reserveEventFd`` and ``singleton.releaseEventFd``).

I know this might sound a bit complicated, but just think about it a while and you'll get it.  :)

# Now what?

For any doubts and questions, don't hesitate to file a ticket to ``valkka-examples`` or ``valkka-core`` repos.

