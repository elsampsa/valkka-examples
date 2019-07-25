from valkka.onvif import OnVif, getWSDLPath

# (1) create your own class:

class DeviceManagement(OnVif):
    namespace = "http://www.onvif.org/ver10/device/wsdl"
    wsdl_file = getWSDLPath("devicemgmt.wsdl")
    sub_xaddr = "device_service"
    port      = "DeviceBinding"


# (2) instantiate your class:

device_service = DeviceManagement(
    ip          = "192.168.0.24",
    port        = 80,
    user        = "admin",
    password    = "12345"
    )

