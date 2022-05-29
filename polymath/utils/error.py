from enum import Enum, EnumMeta

class ErrorMeta(EnumMeta):
    def __call__(cls, value, names=None, *, module=None, qualname=None, type=None, start=1):
        if value.__class__ is str:
            for e in cls:
                if e.value[0] == value.upper():
                    value = e.value
                    break
        return super().__call__(value, names=names, module=module, qualname=qualname, type=type, start=start)


class Error(Enum, metaclass=ErrorMeta):
    @property
    def name(self):
        return self._value_[0]