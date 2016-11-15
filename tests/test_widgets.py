# encoding: utf-8

from django.test import TestCase

from taggit.models import Tag
from test_app.models import Content, MyContent, MyCustomTag

from taggit_labels.widgets import LabelWidget


class LabelTest(TestCase):

    def setUp(self):
        Tag.objects.create(name="Python", slug="python")
        Tag.objects.create(name="Django", slug="django")
        Tag.objects.create(name="Advanced Computering",
                           slug="advanced-computering")
        MyCustomTag.objects.create(name="Coffee", slug="coffee")
        MyCustomTag.objects.create(name="Tea", slug="tea")
        MyCustomTag.objects.create(name="À bientôt", slug="a-bientot")
        self.article = Content.objects.create(title="My test")
        self.article.tags.add("Python")
        self.post = MyContent.objects.create(title="My test")
        self.post.tags.add("Coffee")

    def test_initialization(self):
        customized_widget = LabelWidget(model=MyCustomTag)
        self.assertEqual(customized_widget.model, MyCustomTag)
        default_widget = LabelWidget()
        self.assertEqual(default_widget.model, Tag)

    def test_selected_tags(self):
        widget = LabelWidget()
        return_list = widget.tag_list([getattr(t, widget.lookup_field, '')
                                       for t in self.article.tags.all()])
        self.assertEqual(["python"], [tag['value_field'] for tag in return_list
                                      if tag['field_class'] == 'selected'])
        self.assertEqual(["django", "advanced-computering"],
                         [tag['value_field'] for tag in return_list
                          if tag['field_class'] == ''])

    def test_custom_selected_tags(self):
        widget = LabelWidget(model=MyCustomTag)
        return_list = widget.tag_list([getattr(t, widget.lookup_field, '')
                                       for t in self.post.tags.all()])
        self.assertEqual(["coffee"], [tag['value_field'] for tag in return_list
                                      if tag['field_class'] == 'selected'])
        self.assertEqual(["tea"], [tag['value_field'] for tag in return_list
                                   if tag['field_class'] == ''])

    def test_render_new(self):
        """Render method shouldn't error out with missing or string tags"""
        widget = LabelWidget(model=MyCustomTag)
        widget.render("tags", None, attrs={'id': u'id_tags'})
        widget.render("tags", "'My Tag', 'Another tag'",
                      attrs={'id': u'id_tags'})
