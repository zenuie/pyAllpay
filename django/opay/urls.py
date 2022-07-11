from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('', views.create_payment, name='opay'),
    path('success/', views.get_feedback, name='success'),
    path('donate/', views.donate, name='donate')
    # re_path(r'^search/$',views.song_search,name='song_search'),
    # re_path(r'^ajax/search/$',views.ajax_search,name='ajax_search'),
]
