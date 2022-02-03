class Bind:
    def __init__(self, func, *vargs, **kwargs):
        self.__func     = func
        self.__vargs    = vargs
        self.__kwargs   = kwargs

    def __str__(self):
        return "vargs: %s, kwargs: %s" % (repr(self.__vargs), repr(self.__kwargs))

    def __call__(self, *vargs, **kwargs):
        kwargs.update(self.__kwargs)
        return self.__func(*(self.__vargs + vargs), **kwargs)
