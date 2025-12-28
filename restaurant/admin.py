from django.contrib import admin
from .models import Table, MenuItem, Order, OrderItem

# Registering these lets you manage them at /admin
admin.site.register(Table)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)