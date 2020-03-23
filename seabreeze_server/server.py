import remote_object

__all__ = ['SpectrometerManager','SeaBreezeServer']


class SeaBreezeServer(remote_object.server.Server):
    def __init__(self,server_address,emulate=True):
        remote_object.server.Server.__init__(
            self, 
            server_address, 
            SpectrometerManager(emulate=emulate)
        )

# Spectrometer Manager
class SpectrometerManager:
    """Seabreeze Spectrometer Manager
    
    This class is a wrapper for the `seabreeze.cseabreeze` backend
    which allows to myriad of API calls which exist across several
    nested classes to be made on a single object. This allows the
    backend to be accessible over a `remote_object.server.Server`
    TCP server.
    
    This also allows emulation of an OceanOptics spectrometer
    implemented by the `seatease` library.
    
    Before a device can be used, it must first be selected, using
    the `.select_spectrometer(index)` function. All future API
    calls will be made on this selected device, until is it 
    either un-selected (`.deselect_spectrometer()`), or another
    device is selected.
    
    Several common API calls are directly exposed (i.e. list_devices,
    get_wavelengths, etc), but most underlying calls can be made
    using the `.device_call(...)` and `.features_call(...)` methods.
    See those docstrings for details.
    
    
    :param emulate: bool
        A boolean indicating that the `seatease` library should
         be used instead of the `seabreeze` library, so as to 
         emulate in software a spectrometer device.
         
    Example Usage::
        
        sm = SpectrometerManager(emulate=True)
        
        # Prints a single, emulated, spectrometer
        print(sm.list_devices())
        
        # Activate the spectrometer
        sm.select_spectrometer(0)
        
        # Prints model number
        print(sm.model)
        
        # Prints current measured intensities
        sm.set_integration_time_micros(10*1000) # 10 ms
        print(sm.get_intensities())
        
        # Same as above
        sm.features_call(
            "spectrometer",
            "set_integration_time_micros",
            10*1000 # 10 ms
        )
        print(sm.features_call(
            "spectrometer",
            "get_intensities"
        ))
        
        # Raises SeaTeaseError, no device selected
        sm.delect_spectrometer()
        sm.get_wavelengths()
        
    """
    def __init__(self,emulate=False):
        if emulate:
            import seatease as sb
            self._sb = sb
            self._error = self._sb.cseatease.SeaTeaseError
            self._backend = self._sb.cseatease.SeaTeaseAPI
        else:
            import seabreeze as sb
            self._sb = sb
            self._error = self._sb.cseabreeze.SeaBreezeError
            self._backend = self._sb.cseabreeze.SeaBreezeAPI
            
        self.deselect_spectrometer()
        
    def __repr__(self):
        num = len(self.list_devices())
        act = str(self._dev)
        return "<Spectrometer Manager : {0} devices: Current: {1}>".format(num,act)
    
    def select_spectrometer(self,index=0):
        """Select a spectrometer for API calls
        
        This method selects which spectrometer the manager will attempt
        to make API calls on. It must be called after instantiating
        the `SpectrometerManager` class, but before any device-specific
        method calls are made.
        
        The index provide must match up with the order of devices
        returned by `.list_devices()`. By default, it selects the 
        first spectrometer found.

        Parameters
        ----------
        index : int
            The index of the device to be selected for use. It 
            corresponds to the ordering of .list_devices(). 
            The default is 0--the first device.
        """
        self._dev = self._backend.list_devices()[index]
    
    def deselect_spectrometer(self):
        """Deselects the current spectrometer
        
        This method removes the internal reference to the
        current spectrometer, so that unplugging it will
        not cause other API calls to make weird errors, but
        rather all return the same 'no selected device' error.
        """
        self._dev = None
        
    def list_devices(self):
        """Lists repr's of available SeaBreezeDevices
        
        This method returns the string representations of 
        each of the available (plugged in) `SeaBreezeDevices`.
        Note, unlike `seabreeze.cseabreeze.SeaBreezeAPI.list_devices()`
        which actually returns a list of the device instances,
        this function only returns the string.

        If the actual list of device instances is required, they 
        are accessible via `._backend.list_devices()`, but this
        is not typically used        

        Returns
        -------
        list of str
            A list of the the repr's of each plugged in
            `SeaBreezeDevice`

        """
        return [str(dev) for dev in self._backend.list_devices()]
    
    def device_call(self,fname,*args,**kwargs):
        """Make a cseabreeze backend device API call
        
        This function exposes the backend `seabreeze.cseabreeze`
        API for a `SeaBreezeDevice` to get attributes and methods.
        The base call signature is:
            
            SeaBreezeDevice(...).fname(*args,**kwargs)
            
        (See cseabreeze backend API for details).

        Parameters
        ----------
        fname : str
            name of the API being requested for the feature ('model')
        args : 
            All positional arguments to be passed to the fname call
        kwargs : 
            All named arguments to be passed to the fname call

        Raises
        ------
        SeaBreezeError
            If no device has been selected, raises error. use .select_spectrometer()

        Returns
        -------
            Whatever the fname call returns.
            
            
        Example Usage
        -------------
            
            sm = SpectrometerManager(emulate=True)
            
            sm.select_spectrometer(0)
            
            # Prints model number,
            #  equivalent to: SeaBreezeDevice(...).model
            print(sm.device_call("model"))

            # Checks if device is open,
            #  equivalent to: SeaBreezeDevice(...).is_open()
            print(sm.device_call("is_open"))            
            
        """
        if self._dev is None:
            raise self._error("No device selected, try .select_spectrometer()")
        method = self._dev.__getattribute__(fname)
        try:
            return_value = method(*args,**kwargs)
        except TypeError as e:
            # Uncallable 'methods' are attributes
            if 'not callable' in e.args[0]:
                return_value = method
            # Raise other TypeErrors
            else:
                raise e
        return return_value 
        
    def features_call(self,feature,fname,*args,**kwargs):
        """Make cseabreeze backend device features API call
        
        This function exposes the backend `seabreeze.cseabreeze`
        API for a `SeaBreezeDevice` using the `.features` functionality.
        The base call signature is:
            
            SeaBreezeDevice(...).features[feature].fname(*args,**kwargs)
            
        (See cseabreeze backend API for details).
        
        By providing the name of the feature (feature) and the name of
        the API call being requested (fname), as well as any arguments
        taht fname requires (*arg, **kwargs)

        Parameters
        ----------
        feature : str
            name of the device feature being requested ('spectrometer',
            'eeprom', etc...)
        fname : str
            name of the API being requested for the feature ('get_wavelengths')
        args : 
            All positional arguments to be passed to the fname call
        kwargs : 
            All named arguments to be passed to the fname call

        Raises
        ------
        SeaBreezeError
            If no device has been selected, raises error. use .select_spectrometer()

        Returns
        -------
            Whatever the fname call returns.
            
        
        Example Usage
        -------------
        
            sm = SpectrometerManager(emulate=True)
            
            sm.select_spectrometer(0)
            
            # Prints wavelengths,
            #  equivalent to: SeaBreezeDevice.features\
            #                                 ['spectrometer'][0]\
            #                                 .get_wavelengths()
            print(sm.features_call(
                "spectrometer",
                "get_wavelengths"
            ))
        """
        if self._dev is None:
            raise self._error("No device selected, try .select_spectrometer()")
        return self._dev.features[feature][0].__getattribute__(fname)(*args,**kwargs)
    
    
    def set_integration_time_micros(self,it):
        return self.features_call("spectrometer","set_integration_time_micros",it)
    
    def get_wavelengths(self):
        return self.features_call("spectrometer","get_wavelengths")
    
    def get_intensities(self):
        return self.features_call("spectrometer","get_intensities")
    
    @property
    def model(self):
        return self.device_call("model")
    
    @property
    def serial_number(self):
        return self.device_call("serial_number")
    
    
# Testing
if __name__ == "__main__":
    HOST, PORT = 'localhost', 9999
    with SeaBreezeServer((HOST, PORT), emulate=True) as server:
        print("Hosting at:",HOST,"|",PORT)
        server.serve_forever()
