class SingletonError(Exception):
    """Exception to be raised when you try to create more than 1 instance of a singleton"""
    pass


class Singleton(type):
    """
    Meta-class that represents a singleton.
    Raises `valcheck.meta_classes.SingletonError` if you try to create more than 1 instance of a singleton.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls in cls._instances:
            raise SingletonError(f"Instance of the singleton already exists for the class '{cls.__name__}'")
        cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

