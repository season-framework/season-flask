from .core import stdClass

class __base__(stdClass):
    def __init__(self, framework, inst):
        self.framework = framework
        self.inst = inst
        self._cache = stdClass()

    def __getattr__(self, attr):
        if attr == '__base__':
            return self

        if attr in self._cache:
            return self._cache[attr]
        
        if attr in self.inst:
            fn = getattr(self.inst, attr)
            obj = fn(self.framework)
            self._cache[attr] = obj
            return obj
        
        return stdClass()