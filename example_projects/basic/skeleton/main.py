"""
main.py : libValkka and multiprocess orchestration example

* Copyright: 2017 [copyright holder]
* Authors  : Sampsa Riikonen
* Date     : 2017
* Version  : 0.1

[copy-paste your license here]

main1 does the following:

- Starts libValkka & reading an IP camera & producing data at the cpp side
- RGB24 images and fragmented mp4 is produced at the cpp side and passed through shared memory to python multiprocesses
- In those multiprocesses you can then do image analysis and simultaneously send fragmented mp4 into, say, a webscket
- The video is simultaneously visualized on your screen

main2:

- Similar to main1, but..

TODO

"""
import logging

import os, time, sys
from valkka import core
from valkka.multiprocess import safe_select


"""A "filterchain" defines the streaming topology,
see here: https://elsampsa.github.io/valkka-examples/_build/html/intro.html#valkka-api

Streamin runs at the cpp level, 
while the toplogy is defined at python level
"""
from skeleton.filterchain import BasicFilterChain

"""RGB24Process, FragMP4Process and ClientProcess read frames from the libValkka
c++ side using shared memory.

ClientProcess further shares the frames with the MasterProcess
"""
from skeleton.multiprocess import RGB24Process, FragMP4Process,\
    MasterProcess, ClientProcess


def main1(address):
    """Starting multiprocesses (aka "forking") must be started 
    before anything else.

    libValkka (and so many other libraries) use multithreading (at the c++ level)
    It's a cardinal sin to first create threads and only after that, do forking.  
    That results in "dangling" multithreads and undefined behaviour
    """
    filterchain = BasicFilterChain( # define filterchain
        address = address,
        slot = 1
    )
    rgb_pars = filterchain.getRGBParameters()
    frag_mp4_pars = filterchain.getFragMP4Parameters()

    # process that receives frag mp4 fragments
    # & prints out info.  Feel free to subclass and use them as you please
    frag_mp4_process = FragMP4Process()
    frag_mp4_process.ignoreSIGINT()
    frag_mp4_process.start()
    
    # process that receives RGB24 images
    rgb_process = RGB24Process()
    rgb_process.ignoreSIGINT()
    rgb_process.start()

    # openglthread is used to dump live video to the screen
    # preserved frames in the memory and at the GPI
    gl_ctx = core.OpenGLFrameFifoContext()
    gl_ctx.n_720p = 20
    gl_ctx.n_1080p = 20
    gl_ctx.n_1440p = 0
    gl_ctx.n_4K = 0
    # .. your max possible buffering time depends
    # on those frames available:
    buffering_time_ms = 200
    # create thread:
    openglthread = core.OpenGLThread(
        "openglthread",
        gl_ctx,
        buffering_time_ms)
    openglthread.startCall()

    # livethread uses Live555
    livethread = core.LiveThread("livethread")
    livethread.startCall()

    # start decoders, creates shmem servers, etc.
    filterchain(
        livethread = livethread,
        openglthread = openglthread
    )
    
    # pass shmem arguments (from the server side) to the client processes
    rgb_process.activateRGB24Client(**rgb_pars)
    frag_mp4_process.activateFMP4Client(**frag_mp4_pars)
    
    rgb_pipe = rgb_process.getPipe()
    
    # multiprocesses derived from valkka.multiprocess.AsyncBackMessageProcess
    # have a slightly different API from multiprocessing.Pipe:
    mp4_pipe = frag_mp4_process.getPipe()
    mp4_pipe_fd = mp4_pipe.getReadFd()
    
    # could be called within the main loop
    # in a real-life application you could do it like this:
    # - your ws server receives a request for fmp4
    # - your ws server process sends a request to main process
    # -.. which then calls this:
    filterchain.activateFragMP4()

    """The circus is ready!

    - C+++ side threads are running
    - Python multiprocesses are running
    
    Start the main process
    """
    while True:
        try:
            # multiplex intercom from two multiprocesses
            rlis = [rgb_pipe, mp4_pipe_fd] 
            r, w, e = safe_select(rlis, [], [], timeout = 1)
            if rgb_pipe in r:
                # there's an incoming message object from the rgb process
                msg = rgb_pipe.recv()
                print("main process: message from rgb process", msg)
            if mp4_pipe_fd in r:
                # incoming message (a python object) from the frag_mp4_process
                msg = mp4_pipe.recv()
            if len(r) < 1:
                # inform that (this) main process is alive
                print("main process: I'm alive")
        except KeyboardInterrupt:
            print("you pressed CTRL-C: I will exit")
            break
    # ******************************************************************
    # ******************************************************************

    print("bye!")
    print("subprocess stop")

    frag_mp4_process.deactivateFMP4Client(
        ipc_index = frag_mp4_pars["ipc_index"]
    )
    frag_mp4_process.stop()
    
    rgb_process.deactivateRGB24Client(
        ipc_index = rgb_pars["ipc_index"]
    )
    rgb_process.stop()
    
    print("livethread stop")
    livethread.stopCall()
    filterchain.close()
    print("openglthread stop")
    openglthread.stopCall()
    print("definite bye!")


def main2(address):
    """Like main1, but..

    - client RGB24 processes receive frames from libValkka cpp side
    - ..and forward them to a common master process (typically, your heavy neural-net detector) 
      that does the heavy analysis for all client processes and returns them bbox and other metadata
    """
    filterchain = BasicFilterChain( # define filterchain
        address = address,
        slot = 1
    )
    rgb_pars = filterchain.getRGBParameters()

    # your resource hog neural net detector you only want to instantiate once
    master_process = MasterProcess()
    master_process.ignoreSIGINT()
    master_process.start()
    
    # client process that receives RGB24 images from libValkka cpp side
    client_process = ClientProcess()
    client_process.ignoreSIGINT()
    client_process.start()

    # openglthread is used to dump live video to the screen
    openglthread = core.OpenGLThread("openglthread")
    openglthread.startCall()

    # livethread uses Live555
    livethread = core.LiveThread("livethread")
    livethread.startCall()

    # start decoders, creates shmem servers, etc.
    filterchain(
        livethread = livethread,
        openglthread = openglthread
    )
    
    # pass shmem arguments (from the libValkka cpp side) to the client processes
    client_process.activateRGB24Client(**rgb_pars)
    client_pipe = client_process.getPipe()

    master_process.registerClientProcess(client_process)
    # ..of course, you could register several client processes

    """The circus is ready!

    - C+++ side threads are running
    - Python multiprocesses are running
    
    Start the main process
    """
    while True:
        try:
            rlis = [client_pipe] 
            r, w, e = safe_select(rlis, [], [], timeout = 1)
            if client_pipe in r:
                # there's an incoming message object from the rgb process
                msg = client_pipe.recv()
                print("main process: message from client process", msg)
            if len(r) < 1:
                # inform that (this) main process is alive
                print("main process: I'm alive")
        except KeyboardInterrupt:
            print("you pressed CTRL-C: I will exit")
            break
    # ******************************************************************
    # ******************************************************************

    print("bye!")
    print("client process stop")
    client_process.stop()
    print("master process stop")
    master_process.stop()
    print("livethread stop")
    livethread.stopCall()
    filterchain.close()
    print("openglthread stop")
    openglthread.stopCall()
    print("definite bye!")


if __name__ == "__main__":
    assert(len(sys.argv) >= 2)
    main1(sys.argv[1])
    # main2(sys.argv[1])
