"""Test cases for the Domain model."""

from django.test import TestCase

from cycle_invoice.common.tests.base import get_default_test_user
from cycle_invoice.contact.tests.models.test_organisation import fake_organisation
from cycle_invoice.web.models import Domain


def fake_domain(save: bool) -> Domain:  # noqa: FBT001
    """Create a fake work type."""
    domain = Domain(
        name="domain.com",
        customer=fake_organisation(save=True)
    )
    if save:
        domain.save(user=get_default_test_user())
    return domain


class DomainTest(TestCase):
    """Test cases for the Domain model."""

    def test_str(self) -> None:
        """Test the __str__ of Domain."""
        self.assertEqual("domain.com", str(fake_domain(save=False)))
