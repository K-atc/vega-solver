import sys

class ProfileCapability:
    ### NOTE: Do not call in pypy3 bacause pypy3 does not support `sys.getsizeof()``
    def profileMemoryUsage(self):
        if 'PyPy' in sys.version:
            print("[!] {}.profileMemoryUsage(): pypy3 is not supported".format(self.__class__.__name__))
            return
        
        print("[*] {} memory usage".format(self.__class__.__name__))
        for v in vars(self).keys():
            print("{}.{} = {:,d}".format(self.__class__.__name__, v.ljust(24, ' '), sys.getsizeof(getattr(self, v))))