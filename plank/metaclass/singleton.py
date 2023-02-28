
class MetaSingleton(type):
    __singleton_key = "_singleton_"

    def __call__(cls):
        if len(args) != 0 or len(kwargs) != 0:
            instance = cls.__new__(cls)
            instance.__init__(*args, **kwargs)
            return instance

        if not hasattr(cls, __singleton_key):
            instance = cls.__new__(cls)
            instance.__init__()
            setattr(cls, _Programs__manager_key, instance)
        return  getattr(cls, _Programs__manager_key)

    @property
    def singleton(cls):
        return cls()