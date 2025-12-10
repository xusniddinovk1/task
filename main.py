from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, ForeignKey, CASCADE
from django.db.models.fields import DateTimeField, CharField, PositiveIntegerField
from django.db.models import Model, ForeignKey, CASCADE, CharField, PositiveIntegerField, IntegerField
from django.core.exceptions import ObjectDoesNotExist
from apps.models import CoffeeSize, Product, Settings

PRODUCT_TYPES = (
    ("coffee", "Coffee & Tea"),
    ("product", "Product"),
)

ORDER_STATUS = (
    ("pending", "Pending"),
    ("paid", "Paid"),
    ("cancelled", "Cancelled"),
    ("completed", "Completed"),
)


class Order(Model):
    user = ForeignKey('apps.User', CASCADE, related_name='orders')
    status = CharField(max_length=20, choices=ORDER_STATUS, default="pending")
    created_at = DateTimeField(auto_now_add=True)

    @property
    def total_amount(self):
        return sum(item.sub_amount for item in self.order_items.all())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Order {self.id} - {self.user.email}"


class OrderItem(Model):
    order = ForeignKey('apps.Order', CASCADE, related_name='order_items')
    product_type = CharField(max_length=20, choices=PRODUCT_TYPES)
    product_id = PositiveIntegerField()
    quantity = IntegerField(default=1)

    def get_product(self):
        try:
            if self.product_type == "coffee":
                return CoffeeSize.objects.get(id=self.product_id)
            return Product.objects.get(id=self.product_id)
        except ObjectDoesNotExist:
            return None

    @property
    def sub_amount(self):
        product = self.get_product()
        if not product:
            return 0

        if self.product_type == "coffee":
            settings = Settings.objects.first()
            percentage = settings.coffee_percentage if settings else 0
            base_price = product.price
            profit = base_price + (base_price * percentage / 100)
            return self.quantity * int(profit)

        return self.quantity * (product.price_discounted or product.price_out)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"{self.product_type} - {self.product_id}"
