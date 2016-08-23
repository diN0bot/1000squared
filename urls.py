from django.conf.urls import include, url
from django.contrib import admin
from catalyze import urls as catalyze_urls


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^catalyze/', include(catalyze_urls))
]
