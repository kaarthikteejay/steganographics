import warnings

class UnsupportedMode(Warning):
    #warn: UnsupportedMode("...").warn()
    #raise: raise UnsupportedMode("...")
    """to be written..."""
    def __init__(self, *args):
        self.args = args
        self.message = "The given image is written in {}, which is an unsupported mode! For more help check out help(image.UnsupportedMode)".format(self.args[0])
    def __str__(self):
        return self.message
    def warn(self):
        warnings.warn(self.args[0], UnsupportedMode)

class CompressionWarning(Warning):
    def __init__(self, *args):
        self.args = args
        if len(self.args)==1:
            self.args = self.args[0]
        self.message = "Using the {} file format will compress the image, which may result in data loss for the {} method. Use DCT to save it as {}, but keep the data.".format(self.args[1],self.args[0],self.args[1])
    def __str__(self):
        return self.message
    def warn(self):
        warnings.warn(self.args, CompressionWarning)

