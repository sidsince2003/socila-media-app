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
    path('messages/', views.message_list, name='message_list'),
    path('messages/<str:username>/', views.chat_view, name='chat_view'),
    path('comment/<str:post_id>/', views.post_comment, name='post_comment'),
    path('lobby/', views.lobby, name='lobby'),
    path('room/', views.room, name='room'),
    path('room/', views.room, name='room'),
    path('create_member/', views.createMember, name='create_member'),
    path('get_member/', views.getMembers, name='get_member'),
    path('delete_member/', views.deleteMember, name='delete_member'),
   

    

]
