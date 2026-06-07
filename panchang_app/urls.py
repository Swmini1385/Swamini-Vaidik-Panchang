from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('panchang/', views.panchang_view, name='panchang'),
    path('masik/', views.masik_view, name='masik'),
    path('sanwar/', views.sanwar_view, name='sanwar'),
    path('shubha-muhurt/', views.shubha_muhurt_view, name='shubha_muhurt'),
    path('kundali/', views.kundali_view, name='kundali'),
    path('kundali/<int:pk>/', views.kundali_detail_view, name='kundali_detail'),
    path('kundali-milan/', views.kundali_milan_view, name='kundali_milan'),
    path('choughadiya/', views.choughadiya_view, name='choughadiya'),
    path('settings/', views.settings_view, name='settings'),
    path('select-language/', views.select_language, name='select_language'),
    path('set-location/', views.set_active_location, name='set_active_location'),
    path('api/locations/', views.api_location_search, name='api_location_search'),
    path('api/locations/save/', views.api_save_location, name='api_save_location'),
    path('api/locations/recent/', views.api_recent_locations, name='api_recent_locations'),
    path('api/locations/<int:pk>/delete/', views.api_delete_location, name='api_delete_location'),
    path('api/locations/<int:pk>/restore/', views.api_restore_location, name='api_restore_location'),
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/json'), name='manifest_json'),
    path('service-worker.js', TemplateView.as_view(template_name='service-worker.js', content_type='application/javascript'), name='service_worker'),
]
