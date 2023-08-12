from django.urls import path
from libro import views

app_name = 'index'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    # List View
    path('authors/', views.AuthorListView.as_view(), name="authors-list"),
    path('books/', views.BookListView.as_view(), name="books-list"),
    path('publishers/', views.PublisherListView.as_view(), name="publishers-list"),
    path('series/', views.SeriesListView.as_view(), name="series-list"),
    # Detail View
    path('be/<int:be_id>/', views.BookEditonDetailView.as_view(), name="book-edition-detail"),
    # Other View
    path('search_book/', views.BookSearchView.as_view(), name="search-book"),
    path('import_book/', views.ImportBookView.as_view(), name="import-book"),
    path('import_book_edition/', views.ImportBookEditionView.as_view(), name="import-book-edition"),
]
