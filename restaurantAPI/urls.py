from django.urls import path, include
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemListView.as_view(), name='menu-items'), 
    path('menu-items/<int:pk>', views.SingleMenuItemRetrieveView.as_view(), name='menu-items-detail'), 
    path('manager/menu-items', views.MenuItemListManagerView.as_view(), name='menu-items-manager'), 
    path('manager/menu-items/<int:pk>', views.SingleMenuItemRetrieveManagerView.as_view(), name='menu-items-detail-manager'), 
]