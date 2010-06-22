import re
from urlparse import urlsplit
from xmlrpclib import ServerProxy, Fault, ProtocolError
from urllib2 import urlopen
from urlparse import urljoin
import socket
import threading
import logging

from BeautifulSoup import BeautifulSoup
from django.contrib.sites.models import Site
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.urlresolvers import reverse

from pingback.models import PingbackClient, DirectoryPing
from pingback.exceptions import PingbackNotConfigured, PingbackError

class PingBackThread(threading.Thread):
    def __init__(self, instance, url, links):
        threading.Thread.__init__(self)
        self.instance = instance
        self.url = url
        self.links = links

    def run(self):
        ctype = ContentType.objects.get_for_model(self.instance)
        socket.setdefaulttimeout(10)
        for link in self.links:
            try:
                PingbackClient.objects.get(url=link, content_type=ctype,
                                           object_id=self.instance.id)
            except PingbackClient.DoesNotExist:
                pingback = PingbackClient(object=self.instance, url=link)
                try:
                    f = urlopen(link)
                    server_url = f.info().get('X-Pingback', '') or \
                                 search_link(f.read(512 * 1024))
                    if server_url:
                        server = ServerProxy(server_url)
                        try:
                            result = server.pingback.ping(self.url, link)
                        except Exception, e:
                            pingback.success = False
                        else:
                            pingback.success = not PingbackError.is_error(result)
                except (IOError, ValueError, Fault), e:
                    pass
                pingback.save()
        socket.setdefaulttimeout(None)


def maybe_call(smth):
    if callable(smth):
        return smth()
    else:
        return smth


def search_link(content):
    match = re.search(r'<link rel="pingback" href="([^"]+)" ?/?>', content)
    return match and match.group(1)


def ping_external_links(content_attr=None,
                        content_func=None,
                        url_attr='get_absolute_url',
                        filtr=lambda x: True):
    """ Pingback client function.

    Arguments:

      - `content_attr` - name of attribute, which contains content with links,
        must be HTML. Can be callable.
      - `content_func` - function or unbound method, which can generate HTML
        from an instance.
      - `url_attr` - name of attribute, which contains url of object. Can be
        callable.
      - `filtr` - function to filter out instances. False will interrupt ping.

    Credits go to Ivan Sagalaev.
    """
    assert(content_attr or content_func)

    def execute_links_ping(instance, **kwargs):
        log = logging.getLogger('pingback')
        log.debug('pinging links')

        if not filtr(instance):
            return
        site = getattr(instance, 'site', Site.objects.get_current())
        if content_attr is None:
            content = content_func(instance)
        else:
            content = maybe_call(getattr(instance, content_attr))
        url = maybe_call(getattr(instance, url_attr))
        if not (url.startswith('http://') or url.startswith('https://')):
            url = '%s://%s%s' % (getattr(settings, 'SITE_PROTOCOL', 'http'),
                                 site.domain, url)

        def is_external(external, url):
            path_e = urlsplit(external)[2]
            path_i = urlsplit(url)[2]
            return path_e != path_i

        soup = BeautifulSoup(content)
        links = [a['href'] for a in soup.findAll('a') if is_external(a['href'], url)]

        log.debug('URL %s, pinging all these links: %r' % (url, links))
        pbt = PingBackThread(instance=instance, url=url, links=links)
        pbt.start()
    return execute_links_ping


def ping_directories(content_attr=None,
                     content_func=None,
                     url_attr='get_absolute_url',
                     filtr=lambda x: True,
                     feed_url_fun=lambda x: reverse('feed', args=['blog'])):
    """Ping blog directories

    Arguments:

      - `content_attr` - name of attribute, which contains content with links,
        must be HTML. Can be callable.
      - `content_func` - function or unbound method, which can generate HTML
        from an instance.
      - `url_attr` - name of attribute, which contains url of object. Can be
        callable.
      - `filtr` - function to filter out instances. False will interrupt ping.
      - `feed_url_fun` - function to find feed url
    """
    assert(content_attr or content_func)

    def execute_dirs_ping(instance, **kwargs):
        log = logging.getLogger('pingback')
        log.debug('pinging directories')

        if not filtr(instance):
            return
        site = getattr(instance, 'site', Site.objects.get_current())
        if content_attr is None:
            content = content_func(instance)
        else:
            content = maybe_call(getattr(instance, content_attr))
        protocol = getattr(settings, 'SITE_PROTOCOL', 'http')
        url = maybe_call(getattr(instance, url_attr))
        feed_url = feed_url_fun(instance)
        domain = site.domain
        feed_url = '%s://%s%s' % (protocol, domain, feed_url)
        blog_url = '%s://%s/' % (protocol, domain)
        url = urljoin(blog_url, url)

        #TODO: execute this code in the thread
        for directory_url in settings.DIRECTORY_URLS:
            log.debug('pinging directory %r' % directory_url)

            ping = DirectoryPing(object=instance, url=directory_url)
            try:
                server = ServerProxy(directory_url)
                try:
                    q = server.weblogUpdates.extendedPing(site.name, blog_url, url, feed_url)
                #TODO: Find out name of exception :-)
                except Exception, ex:
                    try:
                        q = server.weblogUpdates.ping(site.name, blog_url, url)
                    except ProtocolError, e:
                        log.exception('protocol error during directory ping %r' % directory_url)
                        ping.success = False
                        ping.save()
                        return execute_dirs_ping
                if q.get('flerror'):
                    ping.success = False
                    log.error('flerror: %s' % q.get('message', 'no message'))
                else:
                    ping.success = True
            except (IOError, ValueError, Fault, socket.error), e:
                log.exception('error during directory ping %r' % directory_url)
            ping.save()
    return execute_dirs_ping
