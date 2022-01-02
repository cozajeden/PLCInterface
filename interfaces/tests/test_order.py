from django.test import TestCase
from interfaces.models import Order, Status

class OrderTest(TestCase):
    def test_can_place_order(self) -> None:
        """
        Test if order is placed correctly
        """
        order, success = Order.objects.place_order(
            interface_name='interface1',
            order_number=1,
            requested_amount=10
        )
        self.assertTrue(success)
        self.assertEqual(order.status, Status.objects.get(status='requested'))
        self.assertEqual(order.requested_amount, 10)
        self.assertEqual(order.completed_amount, 0)
        self.assertEqual(order.number, 1)

    def test_can_update_completed_amount(self) -> None:
        """
        Test if completed_amount is updated correctly
        """
        Order.objects.place_order(
            interface_name='interface1',
            order_number=2,
            requested_amount=10
        )
        Order.objects.update_order('interface1', 2, 6)
        order = Order.objects.get(number=2)
        self.assertEqual(order.completed_amount, 4)
        self.assertEqual(order.status, Status.objects.get(status='requested'))

    def test_can_update_status_to_finished(self) -> None:
        """
        Test if status is updated correctly
        """
        Order.objects.place_order(
            interface_name='interface1',
            order_number=3,
            requested_amount=10
        )
        Order.objects.update_order('interface1', 3, 0)
        order = Order.objects.get(number=3)
        self.assertEqual(order.status, Status.objects.get(status='finished'))

    def test_new_order_sets_other_orders_status_to_stopped(self) -> None:
        """
        Test if status of other orders is updated correctly
        """
        Order.objects.place_order(
            interface_name='interface1',
            order_number=4,
            requested_amount=10
        )
        Order.objects.place_order(
            interface_name='interface1',
            order_number=5,
            requested_amount=10
        )
        order = Order.objects.get(number=4)
        self.assertEqual(order.status, Status.objects.get(status='stopped'))