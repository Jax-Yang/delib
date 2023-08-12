from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import FormView, DetailView
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from common.utils import insert_db_data, insert_author_db, insert_update_be_db_data
from libro.forms import URLCheckForm, BookEditonURLImportForm, BookSearchParamForm
from libro.models import Author, Book, BookEdition, Publisher, Series


# Create your views here.
class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['books_num'] = Book.objects.count()
        context['editions_num'] = BookEdition.objects.count()
        context['authors_num'] = Author.objects.count()
        context['publishers_num'] = Publisher.objects.count()
        return context


class AuthorListView(ListView):
    model = Author
    template_name = "author_list.html"
    context_object_name = 'authors'
    ordering = "-id"


class PublisherListView(ListView):
    model = Publisher
    template_name = "publisher_list.html"
    context_object_name = 'publishers'


class BookListView(ListView):
    context_object_name = 'books'
    template_name = 'book_list.html'

    def get_queryset(self):
        books = Book.objects.defer('created_time', 'updated_time').order_by('-created_time')
        return books


class SeriesListView(ListView):
    context_object_name = 'series'
    template_name = 'series_list.html'
    model = Series


class ImportBookView(FormView):
    template_name = "import_book.html"
    form_class = URLCheckForm
    success_url = reverse_lazy('index:import-book')

    def form_valid(self, form):
        url = form.cleaned_data['url']
        site = form.cleaned_data['type']
        kind = form.cleaned_data['kind']
        if kind == "book":
            if site == "db":
                insert_db_data(url)
            messages.info(self.request, f'Successfully import the Book!!😁😁😁')
        elif kind == "author":
            if site == "db":
                insert_author_db(url)
                messages.info(self.request, f'Successfully import the Author!!😁😁😁')
        return super().form_valid(form)

    def form_invalid(self, form):
        for k, v in form.errors.items():
            messages.error(self.request, f'{v[0]}')
        return super().form_invalid(form)


class ImportBookEditionView(FormView):
    template_name = "import_book_edition.html"
    form_class = BookEditonURLImportForm
    success_url = reverse_lazy('index:import-book-edition')

    def form_valid(self, form):
        url = form.cleaned_data['url']
        lang = form.cleaned_data['lang']
        book_id = form.cleaned_data['book_id']
        insert_update_be_db_data(url, book_id, lang)
        messages.info(self.request, 'Successfully import the Book Edition! 😁😁😁')
        return super().form_valid(form)

    def form_invalid(self, form):
        for k, v in form.errors.items():
            messages.error(self.request, f'{v[0]}')
        return super().form_invalid(form)


class BookSearchView(ListView):
    context_object_name = 'books'
    template_name = "book_list.html"
    form_class = BookSearchParamForm

    def get_serach_data(self):
        form = self.form_class({
            'author_name': self.request.GET.get('a'),
            'book_name': self.request.GET.get('b'),
            'series_name': self.request.GET.get('s'),
        })
        return form

    def get_queryset(self):
        form = self.get_serach_data()
        if form.is_valid():
            if form.cleaned_data['author_name']:
                condition = Q(author__name=form.cleaned_data['author_name'])
            elif form.cleaned_data['series_name']:
                condition = Q(series__name=form.cleaned_data['series_name'])
            elif form.cleaned_data['book_name']:
                condition = (
                        Q(title_zh=form.cleaned_data['book_name'])
                        | Q(title_en=form.cleaned_data['book_name'])
                        | Q(title_ori=form.cleaned_data['book_name']))
            else:
                condition = Q()
            books = Book.objects.filter(condition).order_by("-created_time")
        else:
            books = []
        return books


class BookEditonDetailView(DetailView):
    template_name = "book_edition_detail.html"
    context_object_name = 'book_edition'

    def get_object(self, queryset=None):
        be_id = self.kwargs['be_id']
        be = BookEdition.objects.get(id=be_id)
        return be

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['book'] = self.object.book
        return ctx
