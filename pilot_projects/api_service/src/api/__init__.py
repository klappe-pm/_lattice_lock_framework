"""
REST API endpoints for the API service.

Provides CRUD operations for all entities with proper
error handling using Lattice Lock error types.
"""

from dataclasses import asdict
from typing import Any

from src.models import (
    User,
    Product,
    Order,
    OrderItem,
    Payment,
    OrderStatus,
    PaymentStatus,
    PaymentMethod,
    Currency,
)
from src.services import (
    UserService,
    ProductService,
    OrderService,
    PaymentService,
)


class APIError(Exception):
    """Base API error."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(APIError):
    """Resource not found error."""

    def __init__(self, resource: str, resource_id: int) -> None:
        super().__init__(f"{resource} with id {resource_id} not found", 404)


class ValidationError(APIError):
    """Validation error."""

    def __init__(self, message: str) -> None:
        super().__init__(message, 400)


class UserAPI:
    """API endpoints for user management."""

    def __init__(self, user_service: UserService) -> None:
        self._service = user_service

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new user."""
        required_fields = ["email", "password_hash", "first_name", "last_name"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        try:
            user = self._service.create_user(
                email=data["email"],
                password_hash=data["password_hash"],
                first_name=data["first_name"],
                last_name=data["last_name"],
            )
            return self._serialize_user(user)
        except ValueError as e:
            raise ValidationError(str(e))

    def get(self, user_id: int) -> dict[str, Any]:
        """Get a user by ID."""
        user = self._service.get_user(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return self._serialize_user(user)

    def verify(self, user_id: int) -> dict[str, Any]:
        """Verify a user."""
        if not self._service.verify_user(user_id):
            raise NotFoundError("User", user_id)
        user = self._service.get_user(user_id)
        return self._serialize_user(user)

    def _serialize_user(self, user: User) -> dict[str, Any]:
        """Serialize user to dict, excluding sensitive fields."""
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }


class ProductAPI:
    """API endpoints for product catalog."""

    def __init__(self, product_service: ProductService) -> None:
        self._service = product_service

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new product."""
        required_fields = ["sku", "name", "description", "price_cents", "quantity_in_stock", "category"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        try:
            product = self._service.create_product(
                sku=data["sku"],
                name=data["name"],
                description=data["description"],
                price_cents=data["price_cents"],
                quantity_in_stock=data["quantity_in_stock"],
                category=data["category"],
            )
            return self._serialize_product(product)
        except ValueError as e:
            raise ValidationError(str(e))

    def get(self, product_id: int) -> dict[str, Any]:
        """Get a product by ID."""
        product = self._service.get_product(product_id)
        if not product:
            raise NotFoundError("Product", product_id)
        return self._serialize_product(product)

    def list_available(self) -> list[dict[str, Any]]:
        """List all available products."""
        products = self._service.list_available_products()
        return [self._serialize_product(p) for p in products]

    def update_stock(self, product_id: int, quantity_change: int) -> dict[str, Any]:
        """Update product stock."""
        if not self._service.update_stock(product_id, quantity_change):
            raise ValidationError("Cannot update stock (product not found or insufficient quantity)")
        product = self._service.get_product(product_id)
        return self._serialize_product(product)

    def _serialize_product(self, product: Product) -> dict[str, Any]:
        """Serialize product to dict."""
        return {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "description": product.description,
            "price_cents": product.price_cents,
            "quantity_in_stock": product.quantity_in_stock,
            "category": product.category,
            "is_available": product.is_available,
            "created_at": product.created_at.isoformat() if product.created_at else None,
            "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        }


class OrderAPI:
    """API endpoints for order management."""

    def __init__(self, order_service: OrderService) -> None:
        self._service = order_service

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new order."""
        required_fields = ["user_id", "shipping_address", "billing_address"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        order = self._service.create_order(
            user_id=data["user_id"],
            shipping_address=data["shipping_address"],
            billing_address=data["billing_address"],
            notes=data.get("notes", ""),
        )
        return self._serialize_order(order)

    def get(self, order_id: int) -> dict[str, Any]:
        """Get an order by ID."""
        order = self._service.get_order(order_id)
        if not order:
            raise NotFoundError("Order", order_id)
        return self._serialize_order(order)

    def add_item(self, order_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """Add an item to an order."""
        required_fields = ["product_id", "quantity"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        item = self._service.add_item(
            order_id=order_id,
            product_id=data["product_id"],
            quantity=data["quantity"],
        )
        if not item:
            raise ValidationError("Cannot add item (order not found, product not found, or insufficient stock)")
        return self._serialize_order_item(item)

    def confirm(self, order_id: int) -> dict[str, Any]:
        """Confirm an order."""
        if not self._service.confirm_order(order_id):
            raise ValidationError("Cannot confirm order")
        order = self._service.get_order(order_id)
        return self._serialize_order(order)

    def cancel(self, order_id: int) -> dict[str, Any]:
        """Cancel an order."""
        if not self._service.cancel_order(order_id):
            raise ValidationError("Cannot cancel order")
        order = self._service.get_order(order_id)
        return self._serialize_order(order)

    def _serialize_order(self, order: Order) -> dict[str, Any]:
        """Serialize order to dict."""
        items = self._service.get_order_items(order.id)
        return {
            "id": order.id,
            "user_id": order.user_id,
            "status": order.status.value,
            "total_cents": order.total_cents,
            "shipping_address": order.shipping_address,
            "billing_address": order.billing_address,
            "notes": order.notes,
            "items": [self._serialize_order_item(item) for item in items],
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
        }

    def _serialize_order_item(self, item: OrderItem) -> dict[str, Any]:
        """Serialize order item to dict."""
        return {
            "id": item.id,
            "order_id": item.order_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price_cents": item.unit_price_cents,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }


class PaymentAPI:
    """API endpoints for payment processing."""

    def __init__(self, payment_service: PaymentService) -> None:
        self._service = payment_service

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new payment."""
        required_fields = ["order_id", "amount_cents", "currency", "payment_method", "transaction_id"]
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}")

        try:
            payment = self._service.create_payment(
                order_id=data["order_id"],
                amount_cents=data["amount_cents"],
                currency=Currency(data["currency"]),
                payment_method=PaymentMethod(data["payment_method"]),
                transaction_id=data["transaction_id"],
            )
            return self._serialize_payment(payment)
        except ValueError as e:
            raise ValidationError(str(e))

    def get(self, payment_id: int) -> dict[str, Any]:
        """Get a payment by ID."""
        payment = self._service.get_payment(payment_id)
        if not payment:
            raise NotFoundError("Payment", payment_id)
        return self._serialize_payment(payment)

    def process(self, payment_id: int) -> dict[str, Any]:
        """Process a payment."""
        if not self._service.process_payment(payment_id):
            raise ValidationError("Cannot process payment")
        payment = self._service.get_payment(payment_id)
        return self._serialize_payment(payment)

    def refund(self, payment_id: int) -> dict[str, Any]:
        """Refund a payment."""
        if not self._service.refund_payment(payment_id):
            raise ValidationError("Cannot refund payment")
        payment = self._service.get_payment(payment_id)
        return self._serialize_payment(payment)

    def _serialize_payment(self, payment: Payment) -> dict[str, Any]:
        """Serialize payment to dict."""
        return {
            "id": payment.id,
            "order_id": payment.order_id,
            "amount_cents": payment.amount_cents,
            "currency": payment.currency.value,
            "status": payment.status.value,
            "payment_method": payment.payment_method.value,
            "transaction_id": payment.transaction_id,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "processed_at": payment.processed_at.isoformat() if payment.processed_at else None,
        }


__all__ = [
    "APIError",
    "NotFoundError",
    "ValidationError",
    "UserAPI",
    "ProductAPI",
    "OrderAPI",
    "PaymentAPI",
]
