"""Models for the contact app."""
import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from cycle_invoice.common.models import BaseModel

logger = logging.getLogger(__name__)


class Customer(BaseModel):
    """Model representing a customer."""

    address = models.OneToOneField(
        "Address",
        on_delete=models.PROTECT,
        related_name="address",
        verbose_name=_("address"),
        null=True,
        blank=True,
    )
    email = models.EmailField(
        _("email"),
        max_length=255,
        blank=True
    )
    phone = models.CharField(
        _("phone"),
        max_length=20,
        blank=True
    )

    class Meta:
        """Meta options for the Customer model."""

        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        """Return a string representation of the customer."""
        if hasattr(self, "contact"):
            return str(self.contact)
        if hasattr(self, "organisation"):
            return str(self.organisation)
        return _("Customer")

    @property
    def address_block(self) -> str:
        """Return the address block for the customer."""
        if self.address is not None:
            return str(self) + "\n" + address_block(self.address)
        return str(self)


class Organisation(Customer):
    """Model representing an organisation."""

    name = models.CharField(
        _("name"),
        max_length=255,
        unique=True
    )
    uid = models.CharField(
        _("uid"),
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        """Meta options for the Organisation model."""

        verbose_name = _("company")
        verbose_name_plural = _("companies")

    def __str__(self) -> str:
        """Return a string representation of the organisation."""
        return self.name


class Contact(Customer):
    """Model representing a contact."""

    first_name = models.CharField(
        _("first name"),
        max_length=255
    )
    last_name = models.CharField(
        _("last name"),
        max_length=255
    )
    company = models.ManyToManyField(
        Organisation,
        through="CompanyContact"
    )

    class Meta:
        """Meta options for the Contact model."""

        verbose_name = _("contact")
        verbose_name_plural = _("contacts")

    def __str__(self) -> str:
        """Return a string representation of the contact."""
        return f"{self.first_name} {self.last_name}"


class CompanyContact(BaseModel):
    """Model representing a company contact."""

    company = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        verbose_name=_("company")
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE,
        verbose_name=_("contact")
    )
    role = models.CharField(
        _("role"),
        max_length=255
    )

    class Meta:
        """Meta options for the CompanyContact model."""

        verbose_name = _("company contact")
        verbose_name_plural = _("company contacts")
        constraints = [models.UniqueConstraint(fields=["company", "contact"], name="unique_company_contact")]

    def __str__(self) -> str:
        """Return a string representation of the company contact."""
        return f"{self.company} - {self.contact} - {self.role}"


class Address(BaseModel):
    """Model representing an address."""

    additional = models.CharField(
        _("additional"),
        max_length=255,
        blank=True
    )
    street = models.CharField(
        _("street"),
        max_length=255
    )
    number = models.CharField(
        _("number"),
        max_length=10
    )
    city = models.CharField(
        _("city"),
        max_length=255
    )
    zip_code = models.CharField(
        _("zip code"),
        max_length=12
    )
    country = models.CharField(
        _("country"),
        max_length=255
    )

    class Meta:
        """Meta options for the Address model."""

        verbose_name = _("address")
        verbose_name_plural = _("addresses")

    def __str__(self) -> str:
        """Return a string representation of the address."""
        additional = f"{self.additional}, " if self.additional else ""
        return f"{additional}{self.street} {self.number}, {self.zip_code} {self.city}, {self.country}"


def address_block(address: Address) -> str:
    """Return the address block for the given address."""
    additional = f"{address.additional}\n" if address.additional else ""
    return f"{additional}{address.street} {address.number}\n{address.zip_code} {address.city}\n{address.country}"
