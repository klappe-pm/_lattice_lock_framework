"""
Business logic services for the API.

Services implement business rules and coordinate between
models and external systems.
"""

from datetime import datetime, timezone
from typing import Optional

from src.models import (
    Currency,
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentMethod,
    PaymentStatus,
    Product,
    User,
)


class UserService:
    """Service for user management operations."""

    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1

    def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
    ) -> User:
        """Create a new user account."""
        user = User(
            id=self._next_id,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._users[user.id] = user
        self._next_id += 1
        return user

    def get_user(self, user_id: int) -> User | None:
        """Get a user by ID."""
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email address."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    def verify_user(self, user_id: int) -> bool:
        """Mark a user as verified."""
        user = self._users.get(user_id)
        if user:
            user.is_verified = True
            user.updated_at = datetime.now(timezone.utc)
            return True
        return False


class ProductService:
    """Service for product catalog operations."""

    def __init__(self) -> None:
        self._products: dict[int, Product] = {}
        self._next_id = 1

    def create_product(
        self,
        sku: str,
        name: str,
        description: str,
        price_cents: int,
        quantity_in_stock: int,
        category: str,
    ) -> Product:
        """Create a new product."""
        product = Product(
            id=self._next_id,
            sku=sku,
            name=name,
            description=description,
            price_cents=price_cents,
            quantity_in_stock=quantity_in_stock,
            category=category,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._products[product.id] = product
        self._next_id += 1
        return product

    def get_product(self, product_id: int) -> Product | None:
        """Get a product by ID."""
        return self._products.get(product_id)

    def get_product_by_sku(self, sku: str) -> Product | None:
        """Get a product by SKU."""
        for product in self._products.values():
            if product.sku == sku:
                return product
        return None

    def update_stock(self, product_id: int, quantity_change: int) -> bool:
        """Update product stock quantity."""
        product = self._products.get(product_id)
        if product:
            new_quantity = product.quantity_in_stock + quantity_change
            if new_quantity >= 0:
                product.quantity_in_stock = new_quantity
                product.updated_at = datetime.now(timezone.utc)
                return True
        return False

    def list_available_products(self) -> list[Product]:
        """List all available products."""
        return [p for p in self._products.values() if p.is_available and p.quantity_in_stock > 0]


class OrderService:
    """Service for order management operations."""

    def __init__(self, product_service: ProductService) -> None:
        self._orders: dict[int, Order] = {}
        self._order_items: dict[int, list[OrderItem]] = {}
        self._next_id = 1
        self._next_item_id = 1
        self._product_service = product_service

    def create_order(
        self,
        user_id: int,
        shipping_address: str,
        billing_address: str,
        notes: str = "",
    ) -> Order:
        """Create a new order."""
        order = Order(
            id=self._next_id,
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_cents=0,
            shipping_address=shipping_address,
            billing_address=billing_address,
            notes=notes,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self._orders[order.id] = order
        self._order_items[order.id] = []
        self._next_id += 1
        return order

    def add_item(
        self,
        order_id: int,
        product_id: int,
        quantity: int,
    ) -> OrderItem | None:
        """Add an item to an order."""
        order = self._orders.get(order_id)
        product = self._product_service.get_product(product_id)

        if not order or not product:
            return None

        if order.status != OrderStatus.PENDING:
            return None

        if product.quantity_in_stock < quantity:
            return None

        item = OrderItem(
            id=self._next_item_id,
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price_cents=product.price_cents,
            created_at=datetime.now(timezone.utc),
        )
        self._order_items[order_id].append(item)
        self._next_item_id += 1

        order.total_cents += item.quantity * item.unit_price_cents
        order.updated_at = datetime.now(timezone.utc)

        return item

    def confirm_order(self, order_id: int) -> bool:
        """Confirm an order and reserve inventory."""
        order = self._orders.get(order_id)
        if not order or order.status != OrderStatus.PENDING:
            return False

        items = self._order_items.get(order_id, [])
        for item in items:
            if not self._product_service.update_stock(item.product_id, -item.quantity):
                return False

        order.status = OrderStatus.CONFIRMED
        order.updated_at = datetime.now(timezone.utc)
        return True

    def cancel_order(self, order_id: int) -> bool:
        """Cancel an order and restore inventory."""
        order = self._orders.get(order_id)
        if not order or order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            return False

        if order.status == OrderStatus.CONFIRMED:
            items = self._order_items.get(order_id, [])
            for item in items:
                self._product_service.update_stock(item.product_id, item.quantity)

        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        return True

    def get_order(self, order_id: int) -> Order | None:
        """Get an order by ID."""
        return self._orders.get(order_id)

    def get_order_items(self, order_id: int) -> list[OrderItem]:
        """Get items for an order."""
        return self._order_items.get(order_id, [])


class PaymentService:
    """Service for payment processing operations."""

    def __init__(self) -> None:
        self._payments: dict[int, Payment] = {}
        self._next_id = 1

    def create_payment(
        self,
        order_id: int,
        amount_cents: int,
        currency: Currency,
        payment_method: PaymentMethod,
        transaction_id: str,
    ) -> Payment:
        """Create a new payment."""
        payment = Payment(
            id=self._next_id,
            order_id=order_id,
            amount_cents=amount_cents,
            currency=currency,
            status=PaymentStatus.PENDING,
            payment_method=payment_method,
            transaction_id=transaction_id,
            created_at=datetime.now(timezone.utc),
        )
        self._payments[payment.id] = payment
        self._next_id += 1
        return payment

    def process_payment(self, payment_id: int) -> bool:
        """Process a pending payment."""
        payment = self._payments.get(payment_id)
        if not payment or payment.status != PaymentStatus.PENDING:
            return False

        payment.status = PaymentStatus.PROCESSING
        payment.status = PaymentStatus.COMPLETED
        payment.processed_at = datetime.now(timezone.utc)
        return True

    def refund_payment(self, payment_id: int) -> bool:
        """Refund a completed payment."""
        payment = self._payments.get(payment_id)
        if not payment or payment.status != PaymentStatus.COMPLETED:
            return False

        payment.status = PaymentStatus.REFUNDED
        return True

    def get_payment(self, payment_id: int) -> Payment | None:
        """Get a payment by ID."""
        return self._payments.get(payment_id)

    def get_payments_for_order(self, order_id: int) -> list[Payment]:
        """Get all payments for an order."""
        return [p for p in self._payments.values() if p.order_id == order_id]


__all__ = [
    "UserService",
    "ProductService",
    "OrderService",
    "PaymentService",
]
