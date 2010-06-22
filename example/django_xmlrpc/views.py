"""Uses SimpleXMLRPCServer's SimpleXMLRPCDispatcher to serve XML-RPC requests

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
import sys
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from dispatcher import DjangoXMLRPCDispatcher
from decorators import xmlrpc_func, permission_required


# We create a local DEBUG variable from the data in settings.
DEBUG = hasattr(settings, 'XMLRPC_DEBUG') and settings.XMLRPC_DEBUG


# Declare xmlrpcdispatcher correctly depending on our python version
if sys.version_info[:3] >= (2, 5,):
    xmlrpcdispatcher = DjangoXMLRPCDispatcher(allow_none=False, encoding=None)
else:
    xmlrpcdispatcher = DjangoXMLRPCDispatcher()


@xmlrpc_func(returns='string', args=['string'])
def test_xmlrpc(text):
    """Simply returns the args passed to it as a string"""
    return "Here's a response! %s" % str(text)


@csrf_exempt
def handle_xmlrpc(request):
    """Handles XML-RPC requests. All XML-RPC calls should be forwarded here

    request
        The HttpRequest object that carries the XML-RPC call. If this is a
        GET request, nothing will happen (we only accept POST requests)
    """
    from django.shortcuts import render_to_response
    response = HttpResponse()
    if request.method == "POST":
        if DEBUG:
            print request.raw_post_data
        try:
            response.write(
                xmlrpcdispatcher._marshaled_dispatch(request.raw_post_data))
            if DEBUG:
                print response
            return response
        except:
            return HttpResponseServerError()
    else:
        methods = xmlrpcdispatcher.system_listMethods()
        method_list = []

        for method in methods:
            sig_ = xmlrpcdispatcher.system_methodSignature(method)
            sig = {
                'returns': sig_[0],
                'args': ", ".join(sig_[1:]),
            }

            # this just reads your docblock, so fill it in!
            method_help = xmlrpcdispatcher.system_methodHelp(method)

            method_list.append((method, sig, method_help))

        if hasattr(settings, 'XMLRPC_GET_TEMPLATE'):
            # This behaviour is deprecated
            if settings.DEBUG:
                print "Use of settings.XMLRPC_GET_TEMPLATE is deprecated " \
                    + "Please update your code to use django_xmlrpc/templates"
            template = settings.XMLRPC_GET_TEMPLATE
        else:
            template = 'xmlrpc_get.html'
        return render_to_response(template, {'methods': method_list})


# Load up any methods that have been registered with the server in settings
if hasattr(settings, 'XMLRPC_METHODS'):
    for path, name in settings.XMLRPC_METHODS:
        # if "path" is actually a function, just add it without fuss
        if callable(path):
            xmlrpcdispatcher.register_function(path, name)
            continue

        # Otherwise we try and find something that we can call
        i = path.rfind('.')
        module, attr = path[:i], path[i+1:]

        try:
            mod = __import__(module, globals(), locals(), [attr])
        except ImportError, ex:
            raise ImproperlyConfigured, "Error registering XML-RPC method: " \
                + "module %s can't be imported" % module

        try:
            func = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured, 'Error registering XML-RPC method: ' \
                + 'module %s doesn\'t define a method "%s"' % (module, attr)

        if not callable(func):
            raise ImproperlyConfigured, 'Error registering XML-RPC method: ' \
                + '"%s" is not callable in module %s' % (attr, module)

        xmlrpcdispatcher.register_function(func, name)


# Finally, register the introspection and multicall methods with the XML-RPC
# namespace
xmlrpcdispatcher.register_introspection_functions()
xmlrpcdispatcher.register_multicall_functions()
