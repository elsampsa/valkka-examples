
OnVif
=====

*(Your short primer to SOAP and OnVif)*

Intro
-----

OnVif is a remote-control protocol for manipulating IP cameras, developed by `Axis <http://www.axis.com>`_.

You can use it to PTZ (pan-tilt-zoom) the camera, for setting camera's credentials and resolution, and for almost anything else you can imagine.

OnVif is based on `SOAP <https://en.wikipedia.org/wiki/SOAP>`_, i.e. in sending rather complex XML messages between your client computer and the IP camera.  The messages (remote protocol calls), the responses and the parameters, are defined by **WSDL files**, which look like `this <http://www.onvif.org/ver20/ptz/wsdl>`_.

Python OnVif
------------

In Python, the main bottleneck has been finding a decent open source SOAP library that would do the trick.  Recently, things have got a lot easier with the arrival of `Zeep <https://github.com/mvantellingen/python-zeep>`_.

Before Zeep existed, there was a library called `Suds <https://github.com/suds-community/suds>`_, which has become a bit obsolete by now.  A library called `python-onvif <https://github.com/quatanium/python-onvif>`_, in turn, was based on Suds.

That python-onvif module has since then been forked and modded `to work with Zeep <https://github.com/FalkTannhaeuser/python-onvif-zeep>`_.

However, we don't need any of that, since it's a better idea to

**just use Zeep directly**

Use Zeep as your SOAP client, give it the WSDL file and that's about it!

OnVif with Zeep
---------------

Rather than giving you an obscure and complicated OnVif client implementation, it's better that you learn to do this by yourself using Zeep, so let's begin with:

::

    pip3 install zeep

You also need this table to get started:

=========================================== ======================== ========================
WSDL Declaration                            camera http sub address  wsdl file    
=========================================== ======================== ========================
http://www.onvif.org/ver10/device/wsdl      device_service           devicemgmt.wsdl
http://www.onvif.org/ver10/device/wsdl      Media                    media.wsdl
http://www.onvif.org/ver10/events/wsdl      Events                   events.wsdl
http://www.onvif.org/ver20/ptz/wsdl         PTZ                      ptz.wsdl
http://www.onvif.org/ver20/imaging/wsdl     Imaging                  imaging.wsdl
http://www.onvif.org/ver10/deviceIO/wsdl    DeviceIO                 deviceio.wsdl
http://www.onvif.org/ver20/analytics/wsdl   Analytics                analytics.wsdl
=========================================== ======================== ========================


Here is an example on how to use it to instantiate an OnVif service connection to your camera:

::

    from valkka.onvif import OnVifService

    device_service = OnVifService(
        wsdl_file      = "devicemgmt.wsdl",
        wsdl_port      = "DeviceBinding",
        wsdl_namespace = "http://www.onvif.org/ver10/device/wsdl",
        
        sub_addr    = "device_service",
        ip          = "192.168.0.157",
        port        = 80,
        user        = "admin",
        password    = "12345"
        )
    
The implementation if ``OnVifService`` is only a few lines long, please do take a look at it.  The parameters that go in, are:
    
- The remote control protocol is declared / visualized in the link at the first column.  Go to ``http://www.onvif.org/ver10/device/wsdl`` to see the detailed specifications.
- In that specification, we see that ``wsdl_port`` should be ``DeviceBinding``.
- Each SOAP remote control protocol comes with a certain namespace.  This is the same as that address in the first column, so we set ``wsdl_namespace`` to ``http://www.onvif.org/ver10/device/wsdl``.
- We use a local modified version of the wsdl file.  This can be found in the third column, i.e. set ``wsdl_file`` to ``devicemgmt.wsdl`` (these files come included in libValkka).
- Camera's local http subaddress ``sub_addr`` is ``device_service`` (the second column of the table)
- Rest of the parameters define camera's local IP address and credentials

Now you are ready to go!

Let's try a remote protocol call.

If you look at that specification in ``http://www.onvif.org/ver10/device/wsdl``, there is a remote protocol call name ``GetCapabilities``.  Let's call it:

::

    cap = device_service.ws_client.GetCapabilities()
    print(cap)

We can also pass a variable to that ``GetCapabilities`` call.  Variables are nested objects, that must be constructed separately.  Like this: 
    
::
    
    factory = device_service.zeep_client.type_factory("http://www.onvif.org/ver10/schema")
    category = factory.CapabilityCategory("Device")
    cap = device_service.ws_client.GetCapabilities(category)
    print(cap)
    
here we see that namespace ``http://www.onvif.org/ver10/schema`` declares all basic variables used by the wsdl files.

That's about it.  Now you are able to remote control your camera.  


Notes
-----

::

    import isodate
    Timeout = isodate.Duration(seconds = timeout)



