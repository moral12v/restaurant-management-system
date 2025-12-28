from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Table, MenuItem, Order, OrderItem

class RestaurantSystemTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # 1. Create a sample table
        self.table = Table.objects.create(table_number=5, capacity=4, status='available')
        
        # 2. Create a sample menu item
        self.item = MenuItem.objects.create(name="Burger", price=10.00, category="food")

    def test_table_occupied_on_order(self):
        """Test if creating an order makes the table occupied"""
        # Create an order for Table 5
        response = self.client.post(reverse('order-list'), {'table': self.table.id})
        
        # Refresh from DB
        self.table.refresh_from_db()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.table.status, 'occupied')

    def test_clear_table_action(self):
        """Test the custom Clear Table API action"""
        # Occupy the table first
        self.table.status = 'occupied'
        self.table.save()
        
        # Call the custom action
        url = reverse('table-clear-table', kwargs={'pk': self.table.id})
        response = self.client.post(url)
        
        self.table.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.table.status, 'available')

    def test_pdf_bill_exists(self):
        """Test if the PDF generation endpoint returns a success code"""
        url = reverse('table-generate-bill', kwargs={'pk': self.table.id})
        response = self.client.get(url)
        
        # Verify it returns a PDF
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')