import io
from urllib.parse import urlparse
from xml.etree import cElementTree as ET

from bs4 import BeautifulSoup

from .models import Subscription

SSLIFY_HOST_LIST = (
    'youtube.com', 'www.youtube.com'
)


def create_opml(user):
    subs = Subscription.objects.filter(owner=user).select_related('feed')
    opml = ET.Element('opml')
    opml.set('version', '1.1')
    body = ET.SubElement(opml, 'body')
    for sub in subs:
        outline = ET.SubElement(body, 'outline')
        outline.set('text', sub.title)
        outline.set('xmlUrl', sub.feed.href)
    f = io.BytesIO()
    et = ET.ElementTree(opml)
    et.write(f, encoding='utf-8', xml_declaration=True)
    return f.getvalue()


def fix_content(content):
    """
    Parse article content to rewrite it for a better reader experience
    """
    parsed_content = BeautifulSoup(content)
    for img in parsed_content.find_all('img'):
        del img['srcset']
        del img['sizes']
        img['class'].append('img-responsive')

    for div in parsed_content.find_all('div'):
        del div['style']

    for table in parsed_content.find_all('table'):
        table['class'].append('table-responsive')

    for a in parsed_content.find_all('a'):
        a['target'] = '_blank'

    for iframe in parsed_content.find_all('iframe'):
        url = urlparse(iframe['src'])
        if url.scheme != 'https' and url.netloc in SSLIFY_HOST_LIST:
            iframe['src'] = url._replace(scheme='https').geturl()

    return str(parsed_content)
