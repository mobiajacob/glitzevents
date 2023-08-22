from django.urls import re_path,path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    #############################################################<<<<<<<<< LANDING MODULE >>>>>>>>>>>>>>>>>
    path('', views.index, name='index'),
    path('login_main',views.login_main, name='login_main'),
    path('forgotPassword/', views.forgotPassword,name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate,name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword,name='resetPassword'),
    path('logout/', views.logout,name='logout'),
    
    ############################################################ <<<<<<<<< User MODULE >>>>>>>>>>>>>>>>>

    path('user_registration/',views.user_registration,name='user_registration'),
    path('index_user_confirmation/<int:user_id>/',views.index_user_confirmation,name='index_user_confirmation'),
    path('profile_user_creation/',views.profile_user_creation,name='profile_user_creation'),
    
    
  
    path('user_profile',views.user_profile,name='user_profile'),
    path('edit_user_profile/<int:id>',views.edit_user_profile,name='edit_user_profile'), 
    ]