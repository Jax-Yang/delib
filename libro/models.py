import json
import os

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.templatetags.static import static
from django.urls import reverse
from django.utils.html import format_html

from common.models import NameBaseModel
from meta.settings import MEDIA_URL


class Book(models.Model):
    title_zh = models.CharField("Title", max_length=256, blank=True, default='')
    title_en = models.CharField("English Title", max_length=256, blank=True, default='')
    title_ori = models.CharField("Original Title", max_length=256, blank=True, default='')

    length = models.ForeignKey("BookLength", on_delete=models.CASCADE)
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    series = models.ForeignKey("Series", on_delete=models.CASCADE, blank=True, null=True)
    first_pub_date = models.DateField("First Publication", blank=True, null=True)
    first_pub_date_def = models.CharField("Publication Date Accuracy", default='y', max_length=1, blank=True, null=True)
    desc = models.TextField("Description", blank=True, default='')

    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title_zh

    @property
    def covers(self):
        if self.bookedition_set.filter(cover__cover__isnull=False).exists():
            return [f"{MEDIA_URL}{cover}" for cover in self.bookedition_set.values_list('cover__cover', flat=True)]
        else:
            return ""

    @property
    def covers_dict(self):
        if self.bookedition_set.filter(cover__cover__isnull=False).exists():
            data = {}
            for d in self.bookedition_set.values('cover__cover', 'pub_date', 'publisher__name'):
                key = f"{d['publisher__name']} {d['pub_date']}"
                data[key] = f"{MEDIA_URL}{d['cover__cover']}"
            return data
        else:
            return {}

    @property
    def covers_json(self):
        return json.dumps(self.covers_dict)

    def get_pub_date(self):
        if self.first_pub_date:
            if self.first_pub_date_def == 'd':
                return self.first_pub_date.strftime("%Y-%m-%d")
            elif self.first_pub_date_def == 'm':
                return self.first_pub_date.strftime("%Y-%m")
            else:
                return self.first_pub_date.strftime("%Y")
        else:
            return ""

    @property
    def awards(self):
        result = []
        for award in self.awards_set.all():
            award_short = f"{award.year}年 | {award.prize.name}"
            result.append(award_short)
        return result

    def get_absolute_url(self):
        return reverse('admin:libro_book_change', args=[self.id])

    def get_desc_display(self):
        return format_html(self.desc)


class BookEdition(models.Model):
    lang_mapping = {
        "zh": "中文",
        "en": "英文",
        "jp": "日文",
        "de": "德文",
    }
    rating_source_def = (
        ('db', 'normal'),
        ('gr', 'GoodReads'),
        ('am', 'Amazon'),
    )
    rating_source_def_dict = dict(rating_source_def)
    icon_mapping = {
        'db': static('img/rating-source-icon/gr.ico'),
        'gr': static('img/rating-source-icon/gr.ico'),
        'am': static('img/rating-source-icon/am.ico'),
    }
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    publisher = models.ForeignKey('Publisher', on_delete=models.CASCADE)
    page_num = models.PositiveIntegerField("Pages", blank=True, null=True)
    pub_date = models.DateField("Publication Date", blank=True, null=True)
    pub_date_def = models.CharField("Publication Date Accuracy", default='y', max_length=1, blank=True, null=True)
    rating = models.FloatField("Rating", blank=True, default=0.0)
    rating_sum = models.PositiveIntegerField("Ratings", blank=True, default=0)
    rating_source = models.CharField("Rating Source", choices=rating_source_def, max_length=8, blank=True, default="db",
                                     null=True)
    isbn = models.CharField("ISBN", max_length=16, blank=True, default='')
    lang = models.CharField("Language", max_length=32, blank=True, default='')
    data_resource_url = models.URLField("Data Source Page", blank=True, null=True)

    def __str__(self):
        return self.book.title_zh or self.book.title_ori or self.book.title_en

    def get_pub_date(self):
        if self.pub_date_def == 'd':
            return self.pub_date.strftime("%Y-%m-%d")
        elif self.pub_date_def == 'm':
            return self.pub_date.strftime("%Y-%m")
        else:
            return self.pub_date.strftime("%Y")

    def get_lang_display(self):
        return self.lang_mapping.get(self.lang)

    def get_rating_source_name_display(self):
        return self.rating_source_def_dict.get(self.rating_source, '')

    def get_rating_source_icon_url(self):
        return self.icon_mapping.get(self.rating_source, '')

    def get_admin_url(self):
        return reverse('admin:libro_bookedition_change', args=[self.id])


class Author(NameBaseModel):
    name_ori = models.CharField("Original Name", max_length=256, blank=True, default='')
    country = models.CharField("Country", max_length=32)
    birth_place = models.CharField("Birth Place", max_length=64, blank=True, default='')
    intro = models.TextField("Introduction", blank=True, default="")
    birth_date = models.DateField("Birth Date", blank=True, null=True)
    pass_date = models.DateField("End Date", blank=True, null=True)

    def get_absolute_url(self):
        return reverse('admin:libro_author_change', args=[self.id])


class Series(NameBaseModel):

    def get_absolute_url(self):
        return reverse('admin:libro_series_change', args=[self.id])


class Publisher(NameBaseModel):
    name_ori = models.CharField("Original Name", max_length=256, blank=True, default='')
    site = models.URLField("Site Domain", max_length=128, blank=True, default='')

    def __str__(self):
        return self.name or self.name_ori

    def get_admin_url(self):
        return reverse('admin:libro_publisher_change', args=[self.id])


class Prize(NameBaseModel):
    desc = models.TextField("Description", blank=True, default='')


class Awards(models.Model):
    prize = models.ForeignKey(Prize, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField("Prize Year", blank=True, null=True)
    book = models.ForeignKey("Book", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.prize.name}-{self.year}-{self.book}"


class BookLength(models.Model):
    name = models.CharField("Name", max_length=16)

    def __str__(self):
        return self.name


class SubChapter(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    chapter_name_zh = models.CharField("Name", max_length=128, blank=True, default='')
    chapter_name_en = models.CharField("English Name", max_length=256, blank=True, default='')
    chapter_name_ori = models.CharField("Original Name", max_length=256, blank=True, default='')
    chapter_ord = models.PositiveSmallIntegerField("Chapter Order")

    def __str__(self):
        if self.chapter_name_zh:
            if self.chapter_name_ori:
                if self.chapter_name_en:
                    return f"{self.chapter_name_zh} | {self.chapter_name_ori} | {self.chapter_name_en}"
                else:
                    return f"{self.chapter_name_zh} | {self.chapter_name_ori}"
            else:
                return self.chapter_name_zh
        elif self.chapter_name_ori:
            if self.chapter_name_en:
                return f"{self.chapter_name_ori} | {self.chapter_name_en}"
            else:
                return self.chapter_name_ori
        else:
            return self.chapter_name_en


def cover_save_path(instance, filename):
    author_name = instance.book_edition.book.author.name
    publisher_name = instance.book_edition.publisher.name
    name = instance.book_edition.book.title_zh.replace('/', '_')
    pub_date = instance.book_edition.pub_date.strftime("%Y_%m_%d")
    _, ext = os.path.splitext(filename)
    return os.path.join("covers", author_name, publisher_name, f"{name}_{pub_date}{ext}")


class Cover(models.Model):
    cover = models.ImageField(upload_to=cover_save_path, blank=True, null=True)
    book_edition = models.OneToOneField(BookEdition, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return os.path.basename(self.cover.name)


@receiver(pre_save, sender=Cover)
def pre_save_image(sender, instance, *args, **kwargs):
    try:
        old_img = sender.objects.get(id=instance.id).cover.path
        try:
            new_img = instance.cover.path
        except ValueError:
            new_img = None
        if new_img != old_img:
            if os.path.exists(old_img):
                os.remove(old_img)
    except:
        pass
