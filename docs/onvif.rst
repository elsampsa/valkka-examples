
OnVif & Discovery
=================

*(Your short primer to SOAP and OnVif)*

Installing
----------

Onvif and discovery come in a `separate python package <https://github.com/elsampsa/valkka-onvif>`_ which you need to install with:

::

    pip install valkka-onvif


Intro
-----

OnVif is a remote-control protocol for manipulating IP cameras, developed by `Axis <http://www.axis.com>`_.

You can use it to PTZ (pan-tilt-zoom) the camera, for setting camera's credentials and resolution, and for almost anything else you can imagine.

OnVif is based on `SOAP <https://en.wikipedia.org/wiki/SOAP>`_, i.e. on sending rather complex XML messages between your client computer and the IP camera.  
The messages (remote protocol calls), their responses and the parameters, are defined by **WSDL files**, 
which (when visualized nicely) look like `this <http://www.onvif.org/ver20/ptz/wsdl>`_.

Python OnVif with Zeep
----------------------

We use the `Zeep <https://github.com/mvantellingen/python-zeep>`_ opensource SOAP library to communicate with the cameras, with minimum 
extra code on top of Zeep.

You also need this table to get started:

=========================================== ======================== ======================== =================
WSDL Declaration                            Camera http sub address  Wsdl file                Subclass
=========================================== ======================== ======================== =================
http://www.onvif.org/ver10/device/wsdl      device_service           devicemgmt.wsdl          DeviceManagement
http://www.onvif.org/ver10/media/wsdl       Media                    media.wsdl               Media
http://www.onvif.org/ver10/events/wsdl      Events                   events.wsdl              Events
http://www.onvif.org/ver20/ptz/wsdl         PTZ                      ptz.wsdl                 PTZ
http://www.onvif.org/ver20/imaging/wsdl     Imaging                  imaging.wsdl             Imaging
http://www.onvif.org/ver10/deviceIO/wsdl    DeviceIO                 deviceio.wsdl            DeviceIO
http://www.onvif.org/ver20/analytics/wsdl   Analytics                analytics.wsdl           Analytics
=========================================== ======================== ======================== =================

Here is an example on how to create your own class for an OnVif device service, based on the class ``OnVif``:

.. include:: snippets/onvif_test.py_

The implementation of the base class ``OnVif`` is only a few lines long 
(take a look `here <https://github.com/elsampsa/valkka-onvif/blob/master/valkka/onvif/base.py#L81>`_)
and it is based on Zeep.

The things you need for subclassing an OnVif service are:
    
- The remote control protocol is declared / visualized in the link at the first column.  Go to ``http://www.onvif.org/ver10/device/wsdl`` to see the detailed specifications.
- In that specification, we see that the WSDL "port" is ``DeviceBinding``.
- Each SOAP remote control protocol comes with a certain namespace.  This is the same as that address in the first column, so we set ``namespace`` to ``http://www.onvif.org/ver10/device/wsdl``.
- We use a local modified version of the wsdl file.  This can be found in the third column, i.e. set ``wsdl_file`` to ``devicemgmt.wsdl`` (these files come included in ``valkka-onvif``).
- Camera's local http subaddress ``sub_xaddr`` is ``device_service`` (the second column of the table)

Check out for an example subclass in `here <https://github.com/elsampsa/valkka-onvif/blob/master/valkka/onvif/base.py#L135>`_.

Service classes
---------------

You can create your own OnVif subclass as described above.

However, we have done some of the work for you.  Take a look at the column "Subclass" in the table above, and you'll find them:

::

    from valkka.onvif import Media

    media_service = Media(
        ip          = "192.168.0.24",
        port        = 80,
        user        = "admin",
        password    = "12345"
        )


Example call
------------

Let's try a remote protocol call.

If you look at that specification in ``http://www.onvif.org/ver10/device/wsdl``, there is a remote protocol call name ``GetCapabilities``.  Let's call it:

::
    
    from valkka.onvif import DeviceManagement

    device_service = DeviceManagement(
            ip          = "192.168.0.24",
            port        = 80,
            user        = "admin",
            password    = "12345"
            )

    cap = device_service.ws_client.GetCapabilities()
    print(cap)

We can also pass a variable to that ``GetCapabilities`` call - variables 
are nested objects, that must be constructed separately.  Like this: 
    
::
    
    factory = device_service.zeep_client.type_factory("http://www.onvif.org/ver10/schema")
    category = factory.CapabilityCategory("Device")
    cap = device_service.ws_client.GetCapabilities(category)
    print(cap)
    
The namespace ``http://www.onvif.org/ver10/schema`` declares all basic variables used by the wsdl files.  We also provide a short-cut command for that:

::

    category = device_service.getVariable("Device")

That's about it.  Now you are able to remote control your camera.  

One extra bonus: to open the specifications directly with Firefox, try this

::

    device_service.openSpecs()


Onvif Pitfalls
--------------

*Axis cameras*

Although Axis is *the* brand that created OnVif, their cameras are extremely picky on the onvif calls: if your client machine's walltime 
differs even slightly on the camera's time, axis cameras (at least the model I have), reject the call (you'll get "Sender not Authorized").

You need to set (manually) your camera's time equal to your client linux machine's time - up to a second.  One option
is to establish an NTP server on your linux machine and then tell the camera to use that NTP server to synchronize it's time.

*Time durations*

When specifying durations with Zeep, you must use the ``isodate`` module, like this:


::

    import isodate
    timeout = isodate.Duration(seconds = 2)

Now that variable ``timeout`` can be used with OnVif calls.

Discovery
---------

Discovery module uses arp-scan and/or the WSDiscovery protocol.

The API is subject to change and is explained in detail at the `valkka-onvif main readme <https://github.com/elsampsa/valkka-onvif>`_

Most importantly, you need to give normal users the ability to perform arp-scans, so before using discovery tools,
do this:

::

    sudo apt-get install arp-scan
    sudo chmod u+s /usr/sbin/arp-scan
