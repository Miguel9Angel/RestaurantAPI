from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework import generics, permissions
from . import models
from .serializer import MenuItemSerializer
from .permissions import ReadOnlyPremission
# Create your views here.
class MenuItemListView(generics.ListAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class SingleMenuItemRetrieveView(generics.RetrieveAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class MenuItemListManagerView(generics.ListCreateAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAdminUser]

class SingleMenuItemRetrieveManagerView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAdminUser]