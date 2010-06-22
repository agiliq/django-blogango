"""Pingback exceptions"""

class PingbackNotConfigured(Exception):
    pass


class PingbackError(Exception):
    """
    Defines an XML-RPC fault with the appropriate error codes for
    pingback's. These are thrown in the ping method when an error as
    described in the specification occurs. Error codes are taken from
    the specification at http://www.hixie.ch/specs/pingback/pingback

    """

    SOURCE_DOES_NOT_EXIST       = 0x0010
    SOURCE_DOES_NOT_LINK        = 0x0011
    TARGET_DOES_NOT_EXIST       = 0x0020
    TARGET_IS_NOT_PINGABLE      = 0x0021
    PINGBACK_ALREADY_REGISTERED = 0x0030
    ACCESS_DENIED               = 0x0031
    CONNECTION_ERROR            = 0x0032

    def __init__(self, error_code):
        self.error_code = error_code

    @classmethod
    def is_error(cls, value):
        return value in [ 0x0010, 0x0011,  0x0020, 0x0021, 0x0030, 0x0031, 0x0032 ]
