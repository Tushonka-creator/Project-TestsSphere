from django.urls import path
from . import views

app_name = 'tests'

urlpatterns = [
    path('debug-submissions/', views.debug_submissions, name='debug_submissions'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register_view, name='register'),
    path('', views.TestListView.as_view(), name='test_list'),
    path('<slug:slug>/', views.TestDetailView.as_view(), name='test_detail'),
    path('t/<slug:slug>/', views.test_detail, name='detail'),
    path('<slug:slug>/submit/', views.submit_test, name='submit_test'),
    path('result/<int:pk>/', views.test_result, name='test_result'),
]
