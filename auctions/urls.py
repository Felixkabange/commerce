from django.urls import path
from django.conf import settings  
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("add_to_watchlist/<int:id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("bid/<int:id>", views.bid, name="bid"),
    path("closeListing/<int:id>", views.closeListing, name="closeListing"),
    path("addComment/<int:id>", views.addComment, name="addComment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories"),
    path("listings/category/<str:category_name>", views.listings_by_category, name="listings_by_category")


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)