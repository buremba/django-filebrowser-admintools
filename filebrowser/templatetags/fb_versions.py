# coding: utf-8

# imports
import os
import re
import logging


# django imports
from django.template import Library, Node, Variable, VariableDoesNotExist, TemplateSyntaxError
from django.utils.encoding import force_unicode, smart_str

# filebrowser imports
from filebrowser.settings import VERSIONS
from filebrowser.conf import fb_settings
from filebrowser.functions import url_to_path, path_to_url, get_version_path, version_generator
from filebrowser.base import FileObject
from settings import STATIC_URL

register = Library()
logger = logging.getLogger(__name__)


class VersionNode(Node):
    def __init__(self, src, version_prefix, alternative = None):
        self.src = Variable(src)
        if version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'"):
            self.version_prefix = version_prefix[1:-1]
        else:
            self.version_prefix = None
            self.version_prefix_var = Variable(version_prefix)
        self.alternative = alternative

    def render(self, context):
        try:
            source = self.src.resolve(context)
        except VariableDoesNotExist:
            return self.default(context)
        if not self.version_prefix:
            try:
                self.version_prefix = self.version_prefix_var.resolve(context)
            except VariableDoesNotExist:
                return self.default(context)
        try:
            source = force_unicode(source)
            if self.version_prefix is not None:
                version_path = get_version_path(url_to_path(source), self.version_prefix)
                if not os.path.isfile(smart_str(os.path.join(fb_settings.MEDIA_ROOT, version_path))):
                    # create version
                    version_path = version_generator(url_to_path(source), self.version_prefix)
                elif os.path.getmtime(smart_str(os.path.join(fb_settings.MEDIA_ROOT, url_to_path(source)))) > os.path.getmtime(smart_str(os.path.join(fb_settings.MEDIA_ROOT, version_path))):
                    # recreate version if original image was updated
                    version_path = version_generator(url_to_path(source), self.version_prefix, force=True)
            else:
                return path_to_url(source)
            return path_to_url(version_path)
        except Exception as e:
            logger.info(e)
            return self.default(context)

    def default(self, context):
        if self.alternative is not None:
            try:
                return STATIC_URL+Variable(self.alternative).resolve(context)
            except VariableDoesNotExist:
                return None


def version(parser, token):
    """
    Displaying a version of an existing Image according to the predefined VERSIONS settings (see filebrowser settings).
    {% version field_name version_prefix %}

    Use {% version my_image 'medium' %} in order to display the medium-size
    version of an Image stored in a field name my_image.

    version_prefix can be a string or a variable. if version_prefix is a string, use quotes.
    """

    try:
        arg = token.split_contents()
        tag = arg[0]
        src = arg[1]
        version_prefix = arg[2]
        alternative = arg[3] if len(arg) > 3 else None
    except:
        raise TemplateSyntaxError, "%s tag requires 2 arguments" % token.contents.split()[0]
    if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")) and version_prefix.lower()[1:-1] not in VERSIONS:
        raise TemplateSyntaxError, "%s tag received bad version_prefix %s" % (tag, version_prefix)
    return VersionNode(src, version_prefix, alternative)


class VersionObjectNode(Node):
    def __init__(self, src, version_prefix, var_name):
        self.var_name = var_name
        self.src = Variable(src)
        if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")):
            self.version_prefix = version_prefix[1:-1]
        else:
            self.version_prefix = None
            self.version_prefix_var = Variable(version_prefix)

    def render(self, context):
        try:
            source = self.src.resolve(context)
        except VariableDoesNotExist:
            return None
        if self.version_prefix:
            version_prefix = self.version_prefix
        else:
            try:
                version_prefix = self.version_prefix_var.resolve(context)
            except VariableDoesNotExist:
                return None
        try:
            source = force_unicode(source)
            version_path = get_version_path(url_to_path(source), version_prefix)
            if not os.path.isfile(smart_str(os.path.join(fb_settings.MEDIA_ROOT, version_path))):
                # create version
                version_path = version_generator(url_to_path(source), version_prefix)
            elif os.path.getmtime(smart_str(os.path.join(fb_settings.MEDIA_ROOT, url_to_path(source)))) > os.path.getmtime(smart_str(os.path.join(fb_settings.MEDIA_ROOT, version_path))):
                # recreate version if original image was updated
                version_path = version_generator(url_to_path(source), version_prefix, force=True)
            context[self.var_name] = FileObject(version_path)
        except:
            context[self.var_name] = ""
        return ''


def version_object(parser, token):
    """
    Returns a context variable 'version_object'.
    {% version_object field_name version_prefix %}

    Use {% version_object my_image 'medium' %} in order to retrieve the medium
    version of an Image stored in a field name my_image.
    Use {% version_object my_image 'medium' as var %} in order to use 'var' as
    your context variable.

    version_prefix can be a string or a variable. if version_prefix is a string, use quotes.
    """

    try:
        #tag, src, version_prefix = token.split_contents()
        tag, arg = token.contents.split(None, 1)
    except:
        raise TemplateSyntaxError, "%s tag requires arguments" % token.contents.split()[0]
    m = re.search(r'(.*?) (.*?) as (\w+)', arg)
    if not m:
        raise TemplateSyntaxError, "%r tag had invalid arguments" % tag
    src, version_prefix, var_name = m.groups()
    if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")) and version_prefix.lower()[1:-1] not in VERSIONS:
        raise TemplateSyntaxError, "%s tag received bad version_prefix %s" % (tag, version_prefix)
    return VersionObjectNode(src, version_prefix, var_name)


class VersionSettingNode(Node):
    def __init__(self, version_prefix):
        if version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'"):
            self.version_prefix = version_prefix[1:-1]
        else:
            self.version_prefix = None
            self.version_prefix_var = Variable(version_prefix)

    def render(self, context):
        if self.version_prefix:
            version_prefix = self.version_prefix
        else:
            try:
                version_prefix = self.version_prefix_var.resolve(context)
            except VariableDoesNotExist:
                return None
        context['version_setting'] = VERSIONS[version_prefix]
        return ''


def version_setting(parser, token):
    """
    Get Information about a version setting.
    """

    try:
        tag, version_prefix = token.split_contents()
    except:
        raise TemplateSyntaxError, "%s tag requires 1 argument" % token.contents.split()[0]
    if (version_prefix[0] == version_prefix[-1] and version_prefix[0] in ('"', "'")) and version_prefix.lower()[1:-1] not in VERSIONS:
        raise TemplateSyntaxError, "%s tag received bad version_prefix %s" % (tag, version_prefix)
    return VersionSettingNode(version_prefix)


register.tag(version)
register.tag(version_object)
register.tag(version_setting)
