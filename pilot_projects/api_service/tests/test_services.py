"""
Tests for API service business logic.

Validates service layer operations and business rules.
"""

import pytest
from src.models import OrderStatus, PaymentStatus, PaymentMethod, Currency
from src.services import UserService, ProductService, OrderService, PaymentService


class TestUserService:
    """Tests for UserService."""

    def test_create_user(self) -> None:
        """Test creating a user."""
        service = UserService()
        user = service.create_user(
            email="test@example.com",
            password_hash="$2b$12$" + "a" * 53,
            first_name="John",
            last_name="Doe",
        )
        assert user.id == 1
        assert user.email == "test@example.com"

    def test_get_user(self) -> None:
        """Test getting a user by ID."""
        service = UserService()
        created = service.create_user(
            email="test@example.com",
            password_hash="$2b$12$" + "a" * 53,
            first_name="John",
            last_name="Doe",
        )
        retrieved = service.get_user(created.id)
        assert retrieved is not None
        assert retrieved.email == "test@example.com"

    def test_get_user_not_found(self) -> None:
        """Test getting a non-existent user."""
        service = UserService()
        assert service.get_user(999) is None

    def test_verify_user(self) -> None:
        """Test verifying a user."""
        service = UserService()
        user = service.create_user(
            email="test@example.com",
            password_hash="$2b$12$" + "a" * 53,
            first_name="John",
            last_name="Doe",
        )
        assert user.is_verified is False
        assert service.verify_user(user.id) is True
        assert service.get_user(user.id).is_verified is True


class TestProductService:
    """Tests for ProductService."""

    def test_create_product(self) -> None:
        """Test creating a product."""
        service = ProductService()
        product = service.create_product(
            sku="PROD-001",
            name="Test Product",
            description="A test product",
            price_cents=1999,
            quantity_in_stock=100,
            category="Electronics",
        )
        assert product.id == 1
        assert product.sku == "PROD-001"

    def test_update_stock_increase(self) -> None:
        """Test increasing stock."""
        service = ProductService()
        product = service.create_product(
            sku="PROD-001",
            name="Test Product",
            description="A test product",
            price_cents=1999,
            quantity_in_stock=100,
            category="Electronics",
        )
        assert service.update_stock(product.id, 50) is True
        assert service.get_product(product.id).quantity_in_stock == 150

    def test_update_stock_decrease(self) -> None:
        """Test decreasing stock."""
        service = ProductService()
        product = service.create_product(
            sku="PROD-001",
            name="Test Product",
            description="A test product",
            price_cents=1999,
            quantity_in_stock=100,
            category="Electronics",
        )
        assert service.update_stock(product.id, -30) is True
        assert service.get_product(product.id).quantity_in_stock == 70

    def test_update_stock_insufficient(self) -> None:
        """Test that stock cannot go negative."""
        service = ProductService()
        product = service.create_product(
            sku="PROD-001",
            name="Test Product",
            description="A test product",
            price_cents=1999,
            quantity_in_stock=100,
            category="Electronics",
        )
        assert service.update_stock(product.id, -150) is False
        assert service.get_product(product.id).quantity_in_stock == 100


class TestOrderService:
    """Tests for OrderService."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.product_service = ProductService()
        self.order_service = OrderService(self.product_service)
        self.product = self.product_service.create_product(
            sku="PROD-001",
            name="Test Product",
            description="A test product",
            price_cents=1999,
            quantity_in_stock=100,
            category="Electronics",
        )

    def test_create_order(self) -> None:
        """Test creating an order."""
        order = self.order_service.create_order(
            user_id=1,
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )
        assert order.id == 1
        assert order.status == OrderStatus.PENDING
        assert order.total_cents == 0

    def test_add_item_to_order(self) -> None:
        """Test adding an item to an order."""
        order = self.order_service.create_order(
            user_id=1,
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )
        item = self.order_service.add_item(order.id, self.product.id, 2)
        assert item is not None
        assert item.quantity == 2
        assert self.order_service.get_order(order.id).total_cents == 3998

    def test_confirm_order_reserves_inventory(self) -> None:
        """Test that confirming an order reserves inventory."""
        order = self.order_service.create_order(
            user_id=1,
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )
        self.order_service.add_item(order.id, self.product.id, 10)
        assert self.order_service.confirm_order(order.id) is True
        assert self.product_service.get_product(self.product.id).quantity_in_stock == 90
        assert self.order_service.get_order(order.id).status == OrderStatus.CONFIRMED

    def test_cancel_order_restores_inventory(self) -> None:
        """Test that cancelling a confirmed order restores inventory."""
        order = self.order_service.create_order(
            user_id=1,
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )
        self.order_service.add_item(order.id, self.product.id, 10)
        self.order_service.confirm_order(order.id)
        assert self.order_service.cancel_order(order.id) is True
        assert self.product_service.get_product(self.product.id).quantity_in_stock == 100
        assert self.order_service.get_order(order.id).status == OrderStatus.CANCELLED


class TestPaymentService:
    """Tests for PaymentService."""

    def test_create_payment(self) -> None:
        """Test creating a payment."""
        service = PaymentService()
        payment = service.create_payment(
            order_id=1,
            amount_cents=5000,
            currency=Currency.USD,
            payment_method=PaymentMethod.CREDIT_CARD,
            transaction_id="txn_123456",
        )
        assert payment.id == 1
        assert payment.status == PaymentStatus.PENDING

    def test_process_payment(self) -> None:
        """Test processing a payment."""
        service = PaymentService()
        payment = service.create_payment(
            order_id=1,
            amount_cents=5000,
            currency=Currency.USD,
            payment_method=PaymentMethod.CREDIT_CARD,
            transaction_id="txn_123456",
        )
        assert service.process_payment(payment.id) is True
        assert service.get_payment(payment.id).status == PaymentStatus.COMPLETED

    def test_refund_payment(self) -> None:
        """Test refunding a payment."""
        service = PaymentService()
        payment = service.create_payment(
            order_id=1,
            amount_cents=5000,
            currency=Currency.USD,
            payment_method=PaymentMethod.CREDIT_CARD,
            transaction_id="txn_123456",
        )
        service.process_payment(payment.id)
        assert service.refund_payment(payment.id) is True
        assert service.get_payment(payment.id).status == PaymentStatus.REFUNDED

    def test_cannot_refund_pending_payment(self) -> None:
        """Test that pending payments cannot be refunded."""
        service = PaymentService()
        payment = service.create_payment(
            order_id=1,
            amount_cents=5000,
            currency=Currency.USD,
            payment_method=PaymentMethod.CREDIT_CARD,
            transaction_id="txn_123456",
        )
        assert service.refund_payment(payment.id) is False
