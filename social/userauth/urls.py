from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload/', views.upload, name='upload'),
    path('like-post/<str:id>/', views.likes, name='like-post'),
    path('post/<str:id>/', views.home_post, name='home-post'),  # changed '#<str:id>' to proper route
    path('explore/', views.explore, name='explore'),
    path('profile/<str:id_user>/', views.profile, name='profile'),
    path('follow/', views.follow, name='follow'),
    path('delete/<str:id>/', views.delete, name='delete'),
    path('search-results/', views.search_results, name='search_results'),
]
