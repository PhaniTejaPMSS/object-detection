# urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('upload-video/', views.upload_video, name='upload_video'),
    path('index_with_paths/<str:video_path>/<str:video_path_webm>/', views.index_with_paths, name='index_with_paths'),
]

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# urlpatterns = [
#     path('', views.index, name='index'),
#     path('upload-video/', views.upload_video, name='upload_video'),
#     path('video/<str:video_path>/<str:video_path_webm>/', views.index, name='index_with_paths'),
# ]
# path('', views.upload_video, name='upload_video'),