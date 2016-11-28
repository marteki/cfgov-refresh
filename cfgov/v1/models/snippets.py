from django.core.validators import URLValidator
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from taggit.managers import TaggableManager

from wagtail.wagtailsnippets.models import register_snippet
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from ..atomic_elements import molecules

import hashlib


@register_snippet
class Contact(models.Model):
    heading = models.CharField(verbose_name=('Heading'), max_length=255,
                               help_text=("The snippet heading"))
    body = RichTextField(blank=True)

    hash = models.CharField(max_length=32, editable=False)

    contact_info = StreamField([
        ('email', molecules.ContactEmail()),
        ('phone', molecules.ContactPhone()),
        ('address', molecules.ContactAddress()),
    ], blank=True)

    panels = [
        FieldPanel('heading'),
        FieldPanel('body'),
        StreamFieldPanel('contact_info'),
    ]

    def __str__(self):
        return self.heading

    @classmethod
    def get_by_title_slug(self, title, slug):
        return self.objects.get(hash=hashlib.md5(title + ';;' + slug).hexdigest())


class DownloadTag(TaggedItemBase):
    content_object = ParentalKey('v1.Download', related_name='tagged_items')


@register_snippet
class Download(ClusterableModel):
    title = models.CharField(max_length=255)
    desc = RichTextField(verbose_name='Description', blank=True)

    thumbnail = models.ForeignKey(
        'v1.CFGOVImage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    related_file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    related_file_es = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    order_link = models.URLField(blank=True,
                                 help_text='URL to order a few copies of a'
                                           'printed piece.',
                                 validators=[URLValidator])

    bulk_order_link = models.URLField(blank=True,
                                      help_text='URL to order copies of a'
                                                'printed piece in bulk.',
                                      validators=[URLValidator])

    tags = TaggableManager(through=DownloadTag, blank=True)

    hash = models.CharField(max_length=32, editable=False)

    panels = [
        FieldPanel('title'),
        FieldPanel('desc'),
        ImageChooserPanel('thumbnail'),
        DocumentChooserPanel('related_file'),
        DocumentChooserPanel('related_file_es'),
        FieldPanel('order_link'),
        FieldPanel('bulk_order_link'),
        FieldPanel('tags'),
    ]

    def __str__(self):
        return self.title

    @classmethod
    def get_by_title_slug(self, title, slug):
        return self.objects.get(hash=hashlib.md5(title + ';;' + slug).hexdigest())


@receiver(pre_save, sender=Contact)
def set_hash(sender, instance, **kwargs):
    heading = instance.heading
    instance.hash = hashlib.md5(heading).hexdigest()

    if ';;' in instance.heading:
        heading = instance.heading.split(';;')[0]

    instance.heading = heading
