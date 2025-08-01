"""A module for sale models."""

from decimal import Decimal

from django.db import models
from django.db.models import CheckConstraint, Q
from django.utils.translation import gettext_lazy as _

from cycle_invoice.common.models import BaseModel
from cycle_invoice.product.models import Product
from cycle_invoice.subscription.models import Subscription
from cycle_invoice.work.models import WorkType


class DocumentInvoice(BaseModel):
    """Model representing a document invoice."""

    customer = models.ForeignKey(
        "contact.Customer",
        on_delete=models.CASCADE,
        related_name="document_invoice"
    )
    invoice_number = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("invoice number")
    )
    date = models.DateField(
        verbose_name=_("date")
    )
    due_date = models.DateField(
        verbose_name=_("due date")
    )
    header_text = models.TextField(
        verbose_name=_("header text"),
        blank=True
    )
    footer_text = models.TextField(
        verbose_name=_("footer text"),
        blank=True
    )

    class Meta:
        """Meta options for the DocumentInvoice model."""

        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"

    def __str__(self) -> str:
        """Return a string representation of the DocumentInvoice."""
        return f"{self.invoice_number} - {self.customer}"

    @property
    def total_sum(self) -> Decimal:
        """The sum of the totals of all DocumentItems belonging to this invoice."""
        return sum((item.total for item in self.document_item.all()), start=Decimal(0))


class DocumentItem(BaseModel):
    """Model representing a document item."""

    ITEM_TYPE_CHOICES = [
        ("product", "Product"),
        ("subscription", "Subscription"),
        ("work", "Work"),
        ("expense_vehicle", "Vehicle expense"),
    ]
    item_type = models.CharField(
        max_length=20,
        choices=ITEM_TYPE_CHOICES,
        verbose_name=_("Type")
    )
    price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("price")
    )
    quantity = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name=_("quantity")
    )
    discount = models.DecimalField(
        verbose_name=_("discount percent"),
        max_digits=5,
        decimal_places=4,
        default=0
    )
    customer = models.ForeignKey(
        "contact.Customer",
        on_delete=models.CASCADE,
        related_name="document_customer"
    )
    invoice = models.ForeignKey(
        DocumentInvoice,
        on_delete=models.CASCADE,
        related_name="document_item",
        null=True,
        blank=True
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="document_item_product",
        null=True,
        blank=True
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="document_item_subscription",
        null=True,
        blank=True
    )
    comment_title = models.CharField(
        max_length=255,
        verbose_name=_("comment title"),
        blank=True,
        default=""
    )
    comment_description = models.TextField(
        verbose_name=_("comment"),
        blank=True,
        default=""
    )
    vehicle = models.ForeignKey(
        "vehicle.Vehicle",
        on_delete=models.PROTECT,
        related_name="document_item_vehicle",
        null=True,
        blank=True
    )
    work_type = models.ForeignKey(
        WorkType,
        on_delete=models.PROTECT,
        related_name="document_item_work_type",
        null=True,
        blank=True
    )

    class Meta:
        """Meta options for the DocumentItem model."""

        constraints = [
            # Constraint for valid item_type values
            CheckConstraint(
                name="%(app_label)s_%(class)s_validate_item_type",
                check=Q(item_type__in=["product", "subscription", "work", "expense_vehicle"])
            ),

            # PRODUCT constraint
            CheckConstraint(
                name="%(app_label)s_%(class)s_fields_match_product",
                check=(
                              Q(item_type="product") &
                              Q(product__isnull=False) &
                              Q(subscription__isnull=True) &
                              Q(work_type__isnull=True) &
                              Q(vehicle__isnull=True) &
                              Q(comment_title="") &
                              Q(comment_description="")
                      ) | ~Q(item_type="product")
            ),

            # SUBSCRIPTION constraint
            CheckConstraint(
                name="%(app_label)s_%(class)s_fields_match_subscription",
                check=(
                              Q(item_type="subscription") &
                              Q(subscription__isnull=False) &
                              Q(product__isnull=False) &
                              Q(comment_title__isnull=False) & ~Q(comment_title="") &
                              Q(work_type__isnull=True) &
                              Q(vehicle__isnull=True) &
                              Q(comment_description="")
                      ) | ~Q(item_type="subscription")
            ),

            # WORK constraint
            CheckConstraint(
                name="%(app_label)s_%(class)s_fields_match_work",
                check=(
                              Q(item_type="work") &
                              Q(work_type__isnull=False) &
                              Q(comment_title__isnull=False) & ~Q(comment_title="") &
                              Q(product__isnull=True) &
                              Q(subscription__isnull=True) &
                              Q(vehicle__isnull=True)
                      ) | ~Q(item_type="work")
            ),

            # EXPENSE VEHICLE constraint
            CheckConstraint(
                name="%(app_label)s_%(class)s_fields_match_expense_vehicle",
                check=(
                              Q(item_type="expense_vehicle") &
                              Q(vehicle__isnull=False) &
                              Q(comment_title__isnull=False) & ~Q(comment_title="") &
                              Q(comment_description__isnull=False) & ~Q(comment_description="") &
                              Q(product__isnull=True) &
                              Q(subscription__isnull=True) &
                              Q(work_type__isnull=True)
                      ) | ~Q(item_type="expense_vehicle")
            ),
        ]

    @property
    def title(self) -> str:
        """Return the title of the document item."""
        if self.item_type == "product":
            return self.product.name
        if self.item_type == "subscription":
            return f"{self.subscription.product.product.name} ({self.comment_title})"
        if self.item_type == "work":
            return f"{self.work_type.name} ({self.comment_title})"
        if self.item_type == "expense_vehicle":
            return f"Kilometerspesen ({self.comment_title})"
        invalid_error_message = f"Invalid item type: {self.item_type}"
        raise ValueError(invalid_error_message)

    @property
    def description(self) -> str:
        """Return the description of the document item."""
        if self.item_type == "product":
            return self.product.description
        if self.item_type == "subscription":
            return self.subscription.product.product.description
        if self.item_type == "work":
            return self.comment_description
        if self.item_type == "expense_vehicle":
            return self.comment_description
        invalid_error_message = f"Invalid item type: {self.item_type}"
        raise ValueError(invalid_error_message)

    @property
    def price_str(self) -> str:
        """Return the price as a string."""
        return f"{self.price:.2f}"

    @property
    def quantity_str(self) -> str:
        """Return the quantity as a string."""
        if self.quantity == int(self.quantity):
            return str(int(self.quantity))
        return f"{self.quantity:.2f}".rstrip("0").rstrip(".")

    @property
    def total(self) -> Decimal:
        """Return the total price."""
        return round(self.price * self.quantity * (1 - self.discount), 2)

    @property
    def total_str(self) -> str:
        """Return the total price as a string."""
        return f"{self.total:.2f}"

    @property
    def discount_str(self) -> str:
        """Return the discount percentage as a string."""
        return f"{(100 * self.discount):.2f}%" if self.discount != 0 else ""
