from django.db.models import Sum
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsManager, IsDeliveryCrew
from . import models
from . import serializer
# Create your views here.
class MenuItemListView(generics.ListAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = serializer.MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class SingleMenuItemRetrieveView(generics.RetrieveAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = serializer.MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class MenuItemListManagerView(generics.ListCreateAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = serializer.MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

class SingleMenuItemRetrieveManagerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = serializer.MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]
    
class ManagerUserListView(generics.ListAPIView):
    serializer_class = serializer.UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self):
        return User.objects.filter(groups__name='manager')
    

class AddUserToManagerGroupView(APIView):
    permissions_classes = [permissions.IsAuthenticated, IsManager]
    
    def post(self, request):
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error':'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id = user_id)
        except User.DoesNotExist:
            return Response({'error':'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        
        manager_group, created = Group.objects.get_or_create(name='manager')        
        user.groups.add(manager_group)
        return Response({'message': f"User {user.username} added to 'manager' group"}, status=status.HTTP_201_CREATED)

class RemoveUserFromManagerGroupView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]
    
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error':'User not found'})

        try:
            manager_group = Group.objects.get(name='manager')
        except Group.DoesNotExist:
            return Response({'error':'Manager group not found'}, status=status.HTTP_404_NOT_FOUND)

        if manager_group not in user.groups.all():
            return Response({'error':'User is not in the manager group'}, status=status.HTTP_404_NOT_FOUND)

        user.groups.remove(manager_group)
        return Response({'message':f"User {user.username} removed from 'manager' group"}, status=status.HTTP_200_OK)
    
class DeliveryCrewUsersView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get(self, request):
        users = User.objects.filter(groups__name='delivery-crew')
        serialized_users = serializer.UserSerializer(users, many=True)
        return Response(serialized_users.data)

    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        group, _ = Group.objects.get_or_create(name='delivery-crew')
        user.groups.add(group)
        return Response({'message': f"User {user.username} added to 'delivery-crew'"}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            group = Group.objects.get(name='delivery-crew')
        except Group.DoesNotExist:
            return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

        if group not in user.groups.all():
            return Response({'error': 'User is not in the delivery-crew group'}, status=status.HTTP_400_BAD_REQUEST)

        user.groups.remove(group)
        return Response({'message': f"User {user.username} removed from 'delivery-crew'"}, status=status.HTTP_200_OK)

class CartMenuItemsView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializer.CartSerializer

    def get(self, request):
        items = models.Cart.objects.filter(user=request.user)
        serialized_cart = serializer.CartSerializer(items, many=True)
        return Response(serialized_cart.data)
    
    def post(self, request):
        data = request.data.copy()
        menuitem_id = data.get('menuitem')

        try:
            menuitem = models.MenuItem.objects.get(id=menuitem_id)
        except models.MenuItem.DoesNotExist:
            return Response({'error':'The MenuItem not exist'}, status=status.HTTP_404_NOT_FOUND)

        quantity = int(data.get('quantity', 1))
        unit_price = menuitem.price
        total_price = unit_price*quantity

        cart_item = models.Cart.objects.create(
            user = request.user,
            menuitem = menuitem,
            quantity = quantity,
            unit_price = unit_price,
            price = total_price
        )

        return Response(serializer.CartSerializer(cart_item), status=status.HTTP_201_CREATED)

    def delete(self, request):
        items = models.Cart.objects.filter(user=request.user)
        items.delete()
        return Response({'message':'Element succesfully eliminated'}, status=status.HTTP_204_NO_CONTENT)
    
class OrdersListCreateView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializer.OrderSerializer
    
    def get(self, request):
        orders = models.Order.objects.filter(user=request.user)
        serialized_order = serializer.OrderSerializer(orders, many=True)
        return Response(serialized_order.data)
    
    def post(self, request):
        items_cart = models.Cart.objects.filter(user=request.user)
        if not items_cart.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        order = models.Order.objects.create(
            user = request.user,
            total=items_cart.aggregate(total_price=Sum('price'))['total_price'] or 0
        )
        for item in items_cart:
            quantity = item.quantity
            unit_price = item.unit_price
            total_price = quantity*unit_price
            models.OrderItem.objects.create(
                order = order,
                menuitem = item,
                quantity = quantity,
                unit_price = unit_price,
                price = total_price
            )
        items_cart.delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderViewList(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializer.OrderItemSerializer

    def get(self, request, order_id):
        order = get_object_or_404(models.Order, id=order_id)
        if order.user != request.user:
            return Response({'error':'You are not allowed to see this order'}, status=status.HTTP_403_FORBIDDEN)
        
        order_items = models.OrderItem.objects.filter(order=order)
        serializer = self.get_serializer(order_items, many=True)
        return Response(serializer.data)

class AllOrderViewList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated,IsManager]
    serializer_class = serializer.OrderSerializer
    queryset = models.Order.objects.all()

class AllOrdersManagerAPIView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated,IsManager]
    serializer_class = serializer.OrderUpdateSerializer
    queryset = models.Order.objects.all()

class DeleteOrderAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated, IsManager]
    serializer_class = serializer.OrderSerializer
    queryset = models.Order.objects.all()

class ListOrderAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, IsDeliveryCrew]
    serializer_class = serializer.OrderSerializer

    def get(self, request):
        delyvery_orders = models.Order.objects.filter(user=request.user)
        serializer = self.get_serializer(delyvery_orders, many=True)
        return Response(serializer.data)

class UpdateOrderStatusView(generics.UpdateAPIView):
    queryset = models.Order.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsDeliveryCrew]
    serializer_class = serializer.OrderSerializer

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if set(request.data.keys()) != {'status'}:
            return Response(
                {'detail':'Just the status variables is available to edit'},
                status=status.HTTP_400_BAD_REQUEST
            )
        order.status = request.data.get('status')
        order.save()
        return Response({'message':'status updated'},status=status.HTTP_200_OK)