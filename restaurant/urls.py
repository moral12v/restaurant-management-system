from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TableViewSet,
    MenuItemViewSet,
    OrderViewSet,
    OrderItemViewSet,
    dashboard,
    kitchen_view
)

router = DefaultRouter()
router.register(r'tables', TableViewSet)
router.register(r'menu', MenuItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard, name='dashboard'),
    path('kitchen/', kitchen_view, name='kitchen'),
]
