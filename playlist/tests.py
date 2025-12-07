
# Create your tests here.
from django.test import TestCase
from .seeds import calculate_position

class PositionTests(TestCase):
    def test_middle(self):
        self.assertEqual(calculate_position(1.0, 2.0), 1.5)
    def test_first(self):
        self.assertEqual(calculate_position(None, 1.0), 0.0)
    def test_append(self):
        self.assertEqual(calculate_position(3.0, None), 4.0)
