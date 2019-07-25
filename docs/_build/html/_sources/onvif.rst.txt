
OnVif
=====

*(Your short primer to SOAP and OnVif)*

Intro
-----

OnVif is a remote-control protocol for manipulating IP cameras, developed by `Axis <http://www.axis.com>`_.

You can use it to PTZ (pan-tilt-zoom) the camera, for setting camera's credentials and resolution, and for almost anything else you can imagine.

OnVif is based on `SOAP <https://en.wikipedia.org/wiki/SOAP>`_, i.e. on sending rather complex XML messages between your client computer and the IP camera.  The messages (remote protocol calls), the responses and the parameters, are defined by **WSDL files**, which (when visualized nicely) look like `this <http://www.onvif.org/ver20/ptz/wsdl>`_.

Python OnVif
------------

In Python, the main bottleneck was in finding a decent open source SOAP library that would do the trick.  Recently, things have got better with the arrival of `Zeep <https://github.com/mvantellingen/python-zeep>`_.

Before Zeep existed, people used `Suds <https://github.com/suds-community/suds>`_, which has become a bit obsolete by now.  A library called `python-onvif <https://github.com/quatanium/python-onvif>`_ was based on Suds.

That python-onvif module has since then been forked and modded `to work with Zeep <https://github.com/FalkTannhaeuser/python-onvif-zeep>`_.

However, we don't need any of that, since it's a better idea to

**use Zeep directly**

with minimum extra code bloat on top of it.

So, use Zeep as your SOAP client, give it the WSDL file and that's about it.

OnVif with Zeep
---------------

Rather than giving you an obscure OnVif client implementation, you'll learn to do this by yourself using Zeep.  Let's begin with:

::

    pip3 install zeep

You also need this table to get started:

=========================================== ======================== ======================== =================
WSDL Declaration                            Camera http sub address  Wsdl file                Subclass
=========================================== ======================== ======================== =================
http://www.onvif.org/ver10/device/wsdl      device_service           devicemgmt.wsdl          DeviceManagement
http://www.onvif.org/ver10/device/wsdl      Media                    media.wsdl               Media
http://www.onvif.org/ver10/events/wsdl      Events                   events.wsdl              Events
http://www.onvif.org/ver20/ptz/wsdl         PTZ                      ptz.wsdl                 PTZ
http://www.onvif.org/ver20/imaging/wsdl     Imaging                  imaging.wsdl             Imaging
http://www.onvif.org/ver10/deviceIO/wsdl    DeviceIO                 deviceio.wsdl            DeviceIO
http://www.onvif.org/ver20/analytics/wsdl   Analytics                analytics.wsdl           Analytics
=========================================== ======================== ======================== =================

Here is an example on how to create your own class for an OnVif device service, based on the class ``OnVif``:


.. include:: snippets/onvif_test.py_

(the implementation of the base class ``OnVif`` is only a few lines long)

The things you need for (1) subclassing an OnVif service are:
    
- The remote control protocol is declared / visualized in the link at the first column.  Go to ``http://www.onvif.org/ver10/device/wsdl`` to see the detailed specifications.
- In that specification, we see that the WSDL "port" is ``DeviceBinding``.
- Each SOAP remote control protocol comes with a certain namespace.  This is the same as that address in the first column, so we set ``namespace`` to ``http://www.onvif.org/ver10/device/wsdl``.
- We use a local modified version of the wsdl file.  This can be found in the third column, i.e. set ``wsdl_file`` to ``devicemgmt.wsdl`` (these files come included in libValkka).
- Camera's local http subaddress ``sub_xaddr`` is ``device_service`` (the second column of the table)

When you (2) instantiate the class into the ``device_service`` object, you just give the camera's local IP address and credentials


Service classes
---------------

You can create your own OnVif subclass as described above.

However, we have done some of the work for you.  Take a look at the column "Subclass" in the table, and you'll find them:

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

    cap = device_service.ws_client.GetCapabilities()
    print(cap)

We can also pass a variable to that ``GetCapabilities`` call.  

Variables are nested objects, that must be constructed separately.  Like this: 
    
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


Notes
-----

When specifying durations with Zeep, you must use the ``isodate`` module, like this:


::

    import isodate
    timeout = isodate.Duration(seconds = 2)

Now that variable ``timeout`` can be used with OnVif calls

    
    
