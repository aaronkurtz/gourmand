import base64
import hashlib
import hmac
import io
from urllib.parse import urlparse
from xml.etree import cElementTree as ET

from django.conf import settings

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


def get_camo_url(image_url):
    b_url = image_url.encode('utf-8')
    b_key = settings.CAMO_KEY.encode('utf-8')
    digest = hmac.new(b_key, b_url, hashlib.sha1).digest()
    b64digest = base64.urlsafe_b64encode(digest).decode('utf-8').strip('=')
    b64url = base64.urlsafe_b64encode(b_url).decode('utf-8').strip('=')
    return '{}{}/{}'.format(settings.CAMO_PATH, b64digest, b64url)


def fix_content(content):
    """
    Parse article content to rewrite it for a better reader experience
    """
    parsed_content = BeautifulSoup(content, "html.parser")
    CAMO_KEY = settings.CAMO_KEY
    for img in parsed_content.find_all('img'):
        if img.get('src') and CAMO_KEY and urlparse(img['src']).scheme != 'https':
            img['src'] = get_camo_url(img['src'])

        del img['srcset']
        del img['sizes']
        img['class'] = img.get('class', []) + ['img-responsive']

    for div in parsed_content.find_all('div'):
        del div['style']

    for table in parsed_content.find_all('table'):
        table['class'] = table.get('class', []) + ['table-responsive']

    for a in parsed_content.find_all('a'):
        a['target'] = '_blank'

    for iframe in parsed_content.find_all('iframe'):
        url = urlparse(iframe['src'])
        if url.scheme != 'https' and url.netloc in SSLIFY_HOST_LIST:
            iframe['src'] = url._replace(scheme='https').geturl()

    return str(parsed_content)
