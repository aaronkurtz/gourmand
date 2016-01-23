from django import template
from django.utils.safestring import mark_safe
from django.contrib.admin.util import lookup_field
from django.db.models.fields.related import ForeignKey
from django.db.models import ObjectDoesNotExist
from django.core.urlresolvers import reverse, NoReverseMatch
from django.contrib.contenttypes.models import ContentType

register = template.Library()


# https://djangosnippets.org/snippets/2657/
@register.filter
def link_fkey(admin_field):
    fieldname = admin_field.field['field']
    displayed = admin_field.contents()
    obj = admin_field.form.instance
    try:
        fieldtype, attr, value = lookup_field(fieldname, obj, admin_field.model_admin)
    except ObjectDoesNotExist:
        fieldtype = None
    if isinstance(fieldtype, ForeignKey):  # XXX - probably over-simplistic wrt escaping
        try:
            admin_url = get_admin_url(value)
        except NoReverseMatch:
            admin_url = None
        if admin_url:
            displayed = u"<a href='%s'>%s</a>" % (admin_url, displayed)
    return mark_safe(displayed)


# adapted from http://djangosnippets.org/snippets/1916/
def get_admin_url(obj):
    content_type = ContentType.objects.get_for_model(obj.__class__)
    return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model),
                   args=[obj.pk])
