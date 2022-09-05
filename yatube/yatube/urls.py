
from django.contrib import admin
from django.urls import include, path

handler404 = 'core.views.page_not_found'
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'

urlpatterns = [
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    path('', include('posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
]
