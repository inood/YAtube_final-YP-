from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

handler404 = "posts.views.page_not_found"  # noqa
handler500 = "posts.views.server_error"  # noqa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('django.contrib.flatpages.urls')),
]

urlpatterns += [
    path('about-author/', views.flatpage, {'url': '/about-author/'},
         name='about'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'},
         name='terms'),
    path('contacts/', views.flatpage, {'url': '/contacts/'},
         name='contacts'),
    path('', include('posts.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
