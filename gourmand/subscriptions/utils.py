import io
from xml.etree import cElementTree as ET

from .models import Subscription


def create_opml(user):
    subs = Subscription.objects.filter(owner=user).select_related('feed')
    opml = ET.Element('opml')
    opml.set('version', '1.1')
    body = ET.SubElement(opml, 'body')
    for sub in subs:
        outline = ET.SubElement(body, 'outline')
        outline.set('text', sub.feed.title)
        outline.set('xmlUrl', sub.feed.href)
    f = io.BytesIO()
    et = ET.ElementTree(opml)
    et.write(f, encoding='utf-8', xml_declaration=True)
    return f.getvalue()
