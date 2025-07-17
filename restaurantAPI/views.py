from django.contrib.auth.models import User, Group
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsManager
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
    permission_classes = [permissions.IsAdminUser]

class SingleMenuItemRetrieveManagerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = serializer.MenuItemSerializer
    permission_classes = [permissions.IsAdminUser]
    
class ManagerUserListView(generics.ListAPIView):
    serializer_class = serializer.UserSerializer
    permission_classes = [IsManager]

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
    
class DeliveryCrewUserListView(generics.ListAPIView):
    serializer_class = serializer.UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsManager]

    def get_queryset(self):
        return User.objects.filter(groups__name='delivery-crew')