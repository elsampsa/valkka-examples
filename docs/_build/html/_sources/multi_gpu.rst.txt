
Multi-GPU systems
=================

(If you just have monitors connected to a single graphics card, no need to be here)

Introduction
------------

Consider the following setup:

- You have 2 graphic cards (GPUs)
- Each card is connected to 4 monitors
- You want to build a video wall with 8 monitors

The two graphic cards are physically separate entities with their own resources, so it actually makes sense to keep them that way in the software side as well.

For creating such a separation, Linux offers a robust, well-tested and ancient (!) solution: **multiple X-Screens**.

Let's state the example case graphically:

::


            +----> monitor 1-1   |
            |                    |   X-Screen 0
    GPU1  --+----> monitor 1-2   |   Spanning four monitors
            |                    |
            +----> monitor 1-3   |
            |                    |
            +----> monitor 1-4   |
    
    
            +----> monitor 2-1   |
            |                    |   X-Screen 1
    GPU2  --+----> monitor 2-2   |   Spanning four monitors
            |                    |
            +----> monitor 2-3   |
            |                    | 
            +----> monitor 2-4   |
 
 
The advantage of this setup is, that the different GPUs don't have to communicate or cross-over data between them.  In OpenGL, they do not have to share contexes.  The disadvantage is that one can't move a program window from GPU1 to GPU2, just the mouse pointer.

On the contrary, if you form a "macro" desktop (with a single X-Screen), spanning all 8 monitors, prepare yourself for performance bottlenecks.  A nice demo is to run "glxgears" and observe what happens to the framerate when you move the glxgears window from one GPU to another.  For a deeper discussion on the subject, see for example `this page. <https://nouveau.freedesktop.org/wiki/MultiMonitorDesktop/>`_

Unfortunately, many Linux desktop environments (KDE for example) have deprecated their ability to handle several X-Screens: do check out `this <https://bugs.kde.org/show_bug.cgi?id=256242#c60>`_ rather frustrating discussion thread / bug report on the subject.

Our approach
------------

As you learned from the tutorials and from the PyQt testsuite, Valkka uses a dedicated thread (OpenGLThread) to pre-reserve resources from the GPU and to communicate with it.  

In a multi-gpu case, one simply launches an OpenGLThread for each GPU: OpenGLThread takes as a parameter a string defining the connection to the X-server (e.g. ":0.0", ":0.1", .. ":0.n", where n is the GPU number).

It is up to the API user to send the decoded frames to the correct OpenGLThread (and GPU).  A simple example, where all decoded frames are sent to all GPUs in the system can be found in

::

  valkka_examples/api_level_2/qt/
  
    test_studio_3.py


Configuration
-------------

We've been succesful in setting up multi-gpu systems with the following setup:

- Use identical Nvidia graphic cards
- Use the NVidia proprietary driver
- With the *nvidia-settings* applet, configure your system as follows:

  - Do **not** use Xinerama
  - Configure each graphic card as a separate X-screen
  - Use "relative" not "absolute" positioning of the screens and monitors

- Use the Xcfe desktop/window manager instead of Kwin/KDE

  - Can be installed with *sudo apt-get install xubuntu-desktop*
  - Turn off window-manager composition: *Settings Manager -> Window Manager Tweaks -> Compositor -> uncheck Enable Display Compositor* 

- Use PyQt5 version 5.11.2 or greater (you probably have to install with *pip3 install*)

Finally, test the configuration with the PyQt testsuite's "test_studio_3.py"



