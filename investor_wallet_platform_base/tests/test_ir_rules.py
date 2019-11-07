# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .test_iwp_base import IWPBaseCase
from odoo.exceptions import AccessError, ValidationError


class IWPIRulesCase(IWPBaseCase):

    def test_only_iwp_manager_creates_structure(self):
        self.as_iwp_user()
        with self.assertRaises(AccessError):
            self.env["res.partner"].create(
                {"name": "test structure", "is_platform_structure": True}
            )
        self.as_emc_user()
        with self.assertRaises(AccessError):
            self.env["res.partner"].create(
                {"name": "test structure", "is_platform_structure": True}
            )
        self.as_emc_manager()
        with self.assertRaises(AccessError):
            self.env["res.partner"].create(
                {"name": "test structure", "is_platform_structure": True}
            )
        self.as_iwp_manager()
        self.env["res.partner"].create(
            {"name": "test structure", "is_platform_structure": True}
        )

        # todo, check users can still touch normal partners

    def test_uwp_user_access(self):
        self.as_iwp_user()
        partner = self.env["res.users"].browse(self.uid).partner_id

        # own subscription request
        cie_request = self.browse_ref(
            "easy_my_coop.subscription_request_1_demo"
        )
        cie_request.structure  # read
        cie_request.write({"name": "write fails"})
        cie_request.create(
            {
                "structure": partner.structure.id,
                "name": "test subscriber",
                "email": "test.login@test.coop",
                "address": "rue wagner 93",
                "zip_code": "4100",
                "city": "Seraing",
                "country_id": self.ref("base.be"),
                "share_product_id": self.env["product.product"]
                .search(
                    [
                        (
                            "product_tmpl_id",
                            "=",
                            self.ref(
                                "easy_my_coop.product_template_share_type_1_demo"
                            ),
                        )
                    ]
                )
                .id,
                "lang": "en_US",
            }
        )
        with self.assertRaises(AccessError):
            cie_request.unlink()

        coop_city_request = self.browse_ref(
            "investor_wallet_platform_base.subscription_request_2_demo"
        )
        with self.assertRaises(AccessError):
            coop_city_request.structure  # read
        with self.assertRaises(AccessError):
            coop_city_request.write({"name": "write fails"})
        with self.assertRaises(AccessError):
            coop_city_request.create(
                {
                    "structure": self.ref(
                        "investor_wallet_platform_base.res_partner_structure_coopcity_demo"
                    ),
                    "name": "test subscriber",
                    "email": "test.login@test.coop",
                    "address": "rue wagner 93",
                    "zip_code": "4100",
                    "city": "Seraing",
                    "country_id": self.ref("base.be"),
                    "share_product_id": (
                        self.env["product.product"]
                        .search(
                            [
                                (
                                    "product_tmpl_id",
                                    "=",
                                    self.ref(
                                        "investor_wallet_platform_base.product_template_share_type_coopcity_1_demo"
                                    ),
                                )
                            ]
                        )
                        .id
                    ),
                    "lang": "en_US",
                }
            )
        with self.assertRaises(AccessError):
            coop_city_request.unlink()
