"""Offers decorators to make the use of django_xmlrpc a great deal simpler

Authors::
    Graham Binns,
    Reza Mohammadi

Credit must go to Brendan W. McAdams <brendan.mcadams@thewintergrp.com>, who
posted the original SimpleXMLRPCDispatcher to the Django wiki:
http://code.djangoproject.com/wiki/XML-RPC

New BSD License
===============
Copyright (c) 2007, Graham Binns http://launchpad.net/~codedragon

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of the <ORGANIZATION> nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from xmlrpclib import Fault
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _


# Some constants for your pleasure
#XXX: Any standardization?
AUTHENTICATION_FAILED_CODE = 81
PERMISSION_DENIED_CODE = 82


class AuthenticationFailedException(Fault):
    """An XML-RPC fault to be raised when a permission_required authentication
    check fails

    Author
    """
    def __init__(self):
        Fault.__init__(self, AUTHENTICATION_FAILED_CODE,
            _('Username and/or password is incorrect'))


class PermissionDeniedException(Fault):
    """An XML-RPC fault to be raised when a permission_required permission
    check fails
    """
    def __init__(self):
        Fault.__init__(self, PERMISSION_DENIED_CODE, _('Permission denied'))


def xmlrpc_method(returns='string', args=None, name=None):
    """Adds a signature to an XML-RPC function and register it with the dispatcher.

    returns
        The return type of the function. This can either be a string
        description (e.g. 'string') or a type (e.g. str, bool) etc.

    args
        A list of the types of the arguments that the function accepts. These
        can be strings or types or a mixture of the two e.g.
        [str, bool, 'string']
    """
    # Args should be a list
    if args is None:
        args = []


    def _xmlrpc_func(func):
        """Inner function for XML-RPC method decoration. Adds a signature to
        the method passed to it.

        func
            The function to add the signature to
        """
        # If name is not None, register the method with the dispatcher.
        from django_xmlrpc.views import xmlrpcdispatcher
        if name is not None:
            xmlrpcdispatcher.register_function(func, name)

        # Add a signature to the function
        func._xmlrpc_signature = {
            'returns': returns,
            'args': args
            }
        return func

    return _xmlrpc_func

xmlrpc_func = xmlrpc_method


# Don't use this decorator when your service is going to be
# available in an unencrpted/untrusted network.
# Configure HTTPS transport for your web server.
def permission_required(perm=None):
    """Decorator for authentication. Uses Django's built in authentication
    framework to provide authenticated-only and permission-related access
    to XML-RPC methods

    perm
        The permission (as a string) that the user must hold to be able to
        call the function that is decorated with permission_required.
    """
    def _dec(func):
        """An inner decorator. Adds the lookup code for the permission passed
        in the outer method to the function passed to it.

        func
            The function to add the permission check to
        """
        def __authenticated_call(username, password, *args):
            """Inner inner decorator. Adds username and password parameters to
            a given XML-RPC function for authentication and permission
            checking purposes and modifies the method signature appropriately

            username
                The username used for authentication

            password
                The password used for authentication
            """
            try:
                user = authenticate(username=username, password=password)
                if not user:
                    raise AuthenticationFailedException
                if perm and not user.has_perm(perm):
                    raise PermissionDeniedException
            except AuthenticationFailedException:
#                log.error("Authentication Failed for username '%s'" % username)
                raise
            except PermissionDeniedException:
#                log.error(("Permission Denied. Username: '%s', " + \
#                    "Required permission: %s") % (username, perm))
                raise
            except:
#                log.error(traceback.format_exc())
                raise AuthenticationFailedException
            return func(user, *args)

        # Update the function's XML-RPC signature, if the method has one
        if hasattr(func, '_xmlrpc_signature'):
            sig = func._xmlrpc_signature

            # We just stick two string args on the front of sign['args'] to
            # represent username and password
            sig['args'] = (['string'] * 2) + sig['args']
            __authenticated_call._xmlrpc_signature = sig

        # Update the function's docstring
        if func.__doc__:
            __authenticated_call.__doc__ = func.__doc__ + \
                "\nNote: Authentication is required."""
            if perm:
                __authenticated_call.__doc__ += ' this function requires ' \
                                             +  '"%s" permission.' % perm

        return __authenticated_call

    return _dec
