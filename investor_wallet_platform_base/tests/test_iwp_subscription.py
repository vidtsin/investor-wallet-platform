# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .test_iwp_base import IWPBaseCase
from odoo.exceptions import AccessError, ValidationError


class IWPSubscriptionCase(IWPBaseCase):

    def test_create_share_type_as_user_fails(self):
        self.as_emc_user()
        structure = (
            self.env["res.users"]
                .browse(self.uid)
                .partner_id
                .structure
        )
        with self.assertRaises(AccessError):
            self.env["product.template"].create(
                {
                    "name": "Part T - Test",
                    "short_name": "Part T",
                    "is_share": True,
                    "default_share_product": True,
                    "force_min_qty": True,
                    "minimum_quantity": 2,
                    "by_individual": True,
                    "by_company": True,
                    "list_price": 50,
                    "display_on_website": True,
                    "structure": structure.id,
                }
            )

    def test_complete_subscription_flow(self):
        self.as_iwp_manager()
        structure = self.env["res.partner"].create(
            {"name": "test structure", "is_platform_structure": True}
        )

        self.as_emc_manager()
        share = self.env["product.template"].create(
            {
                "name": "Part T - Test",
                "short_name": "Part T",
                "is_share": True,
                "default_share_product": True,
                "force_min_qty": True,
                "minimum_quantity": 2,
                "by_individual": True,
                "by_company": True,
                "list_price": 50,
                "display_on_website": True,
            }
        )

        self.as_emc_user()
        self.env.user.partner_id.structure = structure
        request = self.env["subscription.request"].create(
            {
                "structure": structure.id,
                "name": "test subscriber",
                "email": "test.login@test.coop",
                "address": "rue wagner 93",
                "zip_code": "4100",
                "city": "Seraing",
                "country_id": self.ref("base.be"),
                "share_product_id": share.product_variant_id.id,
                "lang": "en_US",
            }
        )

        request.put_on_waiting_list()
        with self.assertRaises(ValidationError):
            # There is no journal defined for this structure.
            request.validate_subscription_request()

        self.as_iwp_manager()
        structure.account_journal = self.env["account.journal"].create(
            {"name": "test journal", "type": "sale", "code": "TEST_"}
        )

        self.as_emc_user()
        request.validate_subscription_request()
