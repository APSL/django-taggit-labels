from django import forms
try:
    # Django 1.9
    from django.forms.utils import flatatt
except ImportError:
    # Django <1.9
    from django.forms.util import flatatt
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils import six

from taggit.models import Tag
from taggit.utils import edit_string_for_tags


class LabelWidget(forms.TextInput):
    """
    Widget class for rendering an item's tags - and all existing tags - as
    selectable labels.
    """
    template_name = 'taggit_label_widget.html'
    lookup_field = 'slug'
    input_type = 'hidden'
    model = Tag

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None) or self.model
        super(LabelWidget, self).__init__(*args, **kwargs)

    @property
    def is_hidden(self):
        return False

    def get_class(self, value, tags):
        """
        Mark tag label field as selected according to the values list
        :param value: evaluating inclusion tag into selected
        :param tags: all available tags
        """
        return 'selected' if value in tags else ''

    def tag_list(self, tags):
        """
        Generates a list of tags identifying those previously selected.

        Returns a list of python dict with from data:
        <slug tag>, <tag name> and <CSS class name>.

        Changing lookup_field attribute you can filter by other model Tag fields.
        """
        return [
            {'value_field': getattr(tag, self.lookup_field, ''), 'label_field': tag.name,
             'field_class': self.get_class(getattr(tag, self.lookup_field, ''), tags)}
            for tag in self.model.objects.all()
        ]

    def format_value(self, value):
        if value is not None and not isinstance(value, six.string_types):
            value = edit_string_for_tags([o.tag for o in value.select_related("tag")])
        return value

    def get_extra_context_data(self):
        """
        Allow an easy override context before render input field.
        """
        return {}

    def render(self, name, value, attrs={}):
        # Case in which a new form is dispalyed
        if value is None:
            current_tags = []
            formatted_value = ""
            selected_tags = self.tag_list(current_tags)

        # Case in which a form is displayed with submitted but not saved
        # details, e.g. invalid form submission
        elif isinstance(value, six.string_types):
            current_tags = [tag.strip(" \"") for tag in value.split(",") if tag]
            formatted_value = value
            selected_tags = self.tag_list(current_tags)

        # Case in which value is loaded from saved tags
        else:
            current_tags = [o.tag for o in value.select_related("tag")]
            formatted_value = self.format_value(value)
            selected_tags = self.tag_list([getattr(t, self.lookup_field, '') for t in current_tags])

        input_field = super(LabelWidget, self).render(name, formatted_value, attrs)

        if attrs.get('class') is None:
            attrs.update({'class': 'tags taggit-labels'})
        list_attrs = flatatt(attrs)

        context = {
            'input_field': input_field,
            'selected_tags': selected_tags,
            'list_attrs': list_attrs
        }
        context.update(self.get_extra_context_data())

        template_content = render_to_string(self.template_name, context)
        return mark_safe(template_content)

    class Media:
        css = {
            'all': ('css/taggit_labels.css',)
        }
        js = ('js/taggit_labels.js',)
