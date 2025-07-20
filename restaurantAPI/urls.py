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
    path('cart/menu-items', views.CartMenuItemsView.as_view(), name='cart-llist'),
    path('cart/menu-items', views.CartMenuItemsView.as_view(), name='cart-menu-items'),
    path('orders/', views.OrdersListCreateView.as_view(), name='order-get-post'),
    path('orders/<int:order_id>/', views.OrderViewList.as_view(), name='Order-menu-item'),
    path('orders/', views.AllOrderViewList.as_view(), name='all-orders-user'),
    path('orders/', views.AllOrdersManagerAPIView.as_view(), name='all-orders'),
    path('orders/<int:order_id>/', views.DeleteOrderAPIView.as_view(), name='delete-order'),
    path('orders/', views.ListOrderAPIView.as_view(), name='all-orders-delivery-crew'),
    path('orders/<int:order_id>/', views.UpdateOrderStatusView.as_view(), name='patch-order'),
]  