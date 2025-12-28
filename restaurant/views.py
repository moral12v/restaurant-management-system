from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, F
from django.shortcuts import render
from django.http import HttpResponse
from decimal import Decimal

from .models import Table, MenuItem, Order, OrderItem
from .serializers import TableSerializer, MenuItemSerializer, OrderSerializer ,  OrderItemSerializer

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime


# ================= PERMISSIONS =================
class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.groups.filter(name='Manager').exists()


# ================= TABLE VIEWSET =================
class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    @action(detail=True, methods=['post'])
    def checkout(self, request, pk=None):
        table = self.get_object()
        orders = Order.objects.filter(table=table)

        subtotal = OrderItem.objects.filter(order__in=orders).aggregate(
            total=Sum(F('quantity') * F('price_at_order'))
        )['total'] or 0

        tax = subtotal * Decimal('0.10') 
        grand_total = subtotal + tax
        grand_total = float(subtotal) + tax

        table.status = 'available'
        table.save()

        orders.update(status='completed')

        return Response({
            "table": table.table_number,
            "subtotal": subtotal,
            "tax": tax,
            "grand_total": grand_total,
            "status": "PAID"
        })

    @action(detail=True, methods=['get'])
    def generate_bill(self, request, pk=None):
        table = self.get_object()
        orders = Order.objects.filter(table=table)
        items = OrderItem.objects.filter(order__in=orders)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            f'attachment; filename="bill_table_{table.table_number}.pdf"'
        )

        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter

        # ---------- HEADER ----------
        p.setFont("Helvetica-Bold", 20)
        p.drawCentredString(width / 2, height - 50, "THE GRAND RESTAURANT")

        p.setFont("Helvetica", 10)
        p.drawCentredString(width / 2, height - 70, "123 Food Street, India")
        p.drawCentredString(width / 2, height - 85, "Phone: +91 98765 43210")

        p.line(50, height - 100, width - 50, height - 100)

        # ---------- INFO ----------
        p.setFont("Helvetica", 11)
        p.drawString(50, height - 130, f"Table No: {table.table_number}")
        p.drawRightString(
            width - 50,
            height - 130,
            f"Date: {datetime.now().strftime('%d %b %Y %I:%M %p')}"
        )

        # ---------- TABLE HEADER ----------
        y = height - 170
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Item")
        p.drawRightString(300, y, "Qty")
        p.drawRightString(420, y, "Price")
        p.drawRightString(width - 50, y, "Total")

        p.line(50, y - 5, width - 50, y - 5)

        # ---------- ITEMS ----------
        y -= 25
        subtotal = 0
        p.setFont("Helvetica", 11)

        for item in items:
            total = item.quantity * item.price_at_order
            subtotal += total

            p.drawString(50, y, item.menu_item.name)
            p.drawRightString(300, y, str(item.quantity))
            p.drawRightString(420, y, f"₹{item.price_at_order:.2f}")
            p.drawRightString(width - 50, y, f"₹{total:.2f}")

            y -= 20

        tax = subtotal * Decimal('0.10')
        grand_total = subtotal + tax
        grand_total = subtotal + tax

        # ---------- TOTALS ----------
        p.line(300, y - 10, width - 50, y - 10)

        p.drawRightString(420, y - 30, "Subtotal:")
        p.drawRightString(width - 50, y - 30, f"₹{subtotal:.2f}")

        p.drawRightString(420, y - 50, "Tax (10%):")
        p.drawRightString(width - 50, y - 50, f"₹{tax:.2f}")

        p.setFont("Helvetica-Bold", 13)
        p.drawRightString(420, y - 80, "Grand Total:")
        p.drawRightString(width - 50, y - 80, f"₹{grand_total:.2f}")

        # ---------- FOOTER ----------
        p.setFont("Helvetica-Oblique", 10)
        p.drawCentredString(width / 2, 60, "Thank you for dining with us!")
        p.drawCentredString(width / 2, 45, "Please visit again 🙏")

        p.showPage()
        p.save()

        return response
    @action(detail=True, methods=['post'])
    def clear_table(self, request, pk=None):
        table = self.get_object()
        table.status = 'available'
        table.save()
        Order.objects.filter(table=table, status__in=['placed', 'in_kitchen']).update(status='completed')
        return Response({"status": "Table is now ready for a new customer!"})


# ================= MENU =================
class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsManagerOrReadOnly]


# ================= ORDERS =================
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        table_id = request.data.get('table')

        try:
            table = Table.objects.get(id=table_id)
            order = Order.objects.create(table=table)

            table.status = 'occupied'
            table.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "kitchen_group",
                {
                    "type": "order_notification",
                    "message": f"New Order for Table {table.table_number}",
                }
            )

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Table.DoesNotExist:
            return Response({"error": "Table not found"}, status=404)


# ================= DASHBOARD =================
def dashboard(request):
    tables = Table.objects.all().order_by('table_number')
    return render(request, 'restaurant/dashboard.html', {'tables': tables})


def kitchen_view(request):
    orders = Order.objects.filter(status__in=['placed', 'in_kitchen'])
    return render(request, 'restaurant/kitchen.html', {'orders': orders})

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer