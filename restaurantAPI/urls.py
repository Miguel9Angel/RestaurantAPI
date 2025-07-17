from django.urls import path, include
from . import views

urlpatterns = [
    path('menu-items', views.MenuItemListView.as_view(), name='menu-items'), 
    path('menu-items/<int:pk>', views.SingleMenuItemRetrieveView.as_view(), name='menu-items-detail'), 
    path('manager/menu-items', views.MenuItemListManagerView.as_view(), name='menu-items-manager'), 
    path('manager/menu-items/<int:pk>', views.SingleMenuItemRetrieveManagerView.as_view(), name='menu-items-detail-manager'), 
    path('groups/manager/users', views.ManagerUserListView.as_view(), name='manager-user-list'),
    path('groups/manager/users', views.AddUserToManagerGroupView.as_view(), name='add-user-to-manager-group'),
    path('groups/manager/users/<int:user_id>/', views.RemoveUserFromManagerGroupView.as_view(), name='remove-manager-user'),
    path('groups/delivery-crew/users', views.DeliveryCrewUsersView.as_view(), name='delivery-crew-user-list'),
    path('cart/menu-items', views.CartListView.as_view(), name='cart-llist'),
]