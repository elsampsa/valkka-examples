 
## Files in this directory

### Qt main programs
```
test_studio_1.py        Live videos streaming demo for rdp and sdp souces
test_studio_2.py        Like (1) but with floating/ungrouped widgets
test_studio_3.py        Like (2), additionally can move the video to another X-screen (for massive video wall like situations)
test_studio_4.py        Like (3), but streaming is evoked from a Qt menu "on-demand"
test_studio_detector.py 
                        Uses libValkka shmem bridge to stream RGB24 images to an OpenCV
                        movement detector process
test_studio_file.py     Read and play stream from a matroska file.  Combined with a movement detector
                        like in test_studio_detector.py
test_studio_5.py        Simultaneous live streaming, recording and playback in Qt
                        WARNING: this is experimental and kinda complex
```

### Filterchains
```
basic.py                Some example filterchain classes
basic1.py               Some more example filterchain classes
basic2.py               Still some more example filterchain classes
manager.py              Filterchain classes for forking streams on-demand
cast.py                 Demo filterchains for multicasting and recasting as RTSP
valkkafs.py             Filterchains for ValkkaFS applications
port.py                 Defines class ViewPort (book-keeping of window id & x-screen number)
```

### Multiprocessing
```
demo_rgb.py             Used by test_studio_detector.py: the analyzing multiprocess
demo_qthread.py         Used by test_studio_detector.py: converts multiprocess messages
                        to Qt signals
demo_analyzer.py        The OpenCV demo analyzer: used by demo_rgb.py
demo_singleton.py       Used by demo_rgb.py & test_studio_detector.py: global synchronization
                        primitive groups
demo_sync.py            Used by demo_singleton.py: sync primitives group classes
```

### Qt 
```
multiprocessing_demo.py 
                        A stand-alone multiprocessing Qt signal/slot demo (without libValkka stuff)

cpp_thread_demo.py      A custom libValkka thread, created at cpp level, running
                        in python and connecting to Qt signal/slot system
```

### Other
```
demo_base.py            Common widgets for the test_studio demos
playback.py             Playback controller
playwidget.py           Timeline & calendar widget
valkkafs2.py            Widget for managing valkkafs parameters
tools.py                Some tools
```
