# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from .test_iwp_base import TestIWPBase
import logging

_logger = logging.getLogger(__name__)


class TestIWPSubscribe(TestIWPBase):
    def test_subscribe_first_share_success(self):
        structure = self.env.ref(
            "investor_wallet_platform_base"
            ".res_partner_structure_coopiteasy_demo"
        )
        product = self.env.ref(
            "easy_my_coop.product_template_share_type_2_demo"
        )

        self.login("vincent", "demo")

        url = "/struct/%s/subscription" % structure.id
        res = self.http_get(url)
        self.assertEquals(res.status_code, 200)

        data = {
            "shareproduct": product.id,
            "number": 3,
            "total_amount": int(product.list_price * 3),
            "csrf_token": self.get_csrf_token(res),
        }

        res = self.http_post(url=url, data=data)
        self.assertEquals(res.status_code, 200)

        doc = self.html_doc(res)
        alert_success = doc.xpath("//p[contains(@class, 'alert-success')]")
        self.assertTrue(len(alert_success) > 0)

    def test_subscribe_second_share_success(self):
        structure = self.env.ref(
            "investor_wallet_platform_base"
            ".res_partner_structure_coopcity_demo"
        )
        product = self.env.ref(
            "investor_wallet_platform_base"
            ".product_template_share_type_coopcity_1_demo"
        )

        self.login("virginie", "demo")

        url = "/struct/%s/subscription" % structure.id
        res = self.http_get(url)
        self.assertEquals(res.status_code, 200)

        data = {
            "shareproduct": product.id,
            "number": 5,
            "total_amount": int(product.list_price * 3),
            "csrf_token": self.get_csrf_token(res),
        }

        res = self.http_post(url=url, data=data)
        self.assertEquals(res.status_code, 200)

        doc = self.html_doc(res)
        alert_success = doc.xpath("//p[contains(@class, 'alert-success')]")
        if not alert_success:
            try:
                alert_error = doc.xpath("//p[contains(@class, 'alert-danger')]")
                _logger.error(alert_error[0].text.strip())
            except IndexError:
                pass

        self.assertTrue(len(alert_success) > 0)
