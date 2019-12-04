odoo.define('iwp_website.form', function (require) {
    "use strict";

    $(document).ready(function () {
        var manual_share_form = $(".oe_manual_share_form");

        manual_share_form.each(function () {
            var amount_elem = manual_share_form.find("#share_type");
            var qty_elem = manual_share_form.find("#quantity");
            var total_amount_elem = manual_share_form.find("#total_amount");

            function compute_total_amount() {
                var amount = amount_elem[0]
                    .options[amount_elem.prop("selectedIndex")]
                    .dataset
                    .amount;
                var quantity = qty_elem[0].value;
                total_amount_elem[0].value = quantity * amount;
            }

            amount_elem.change(compute_total_amount);
            qty_elem.change(compute_total_amount);
            compute_total_amount();
        });

        var subscription_request_form = $(".oe_subscription_request_form");

        subscription_request_form.each(function () {
            var amount_elem = subscription_request_form.find("#share_type");
            var qty_elem = subscription_request_form.find("#quantity");
            var total_amount_elem = subscription_request_form
                .find("#total_amount");

            function compute_total_amount() {
                var price = amount_elem[0]
                    .options[amount_elem.prop("selectedIndex")]
                    .dataset
                    .price;
                var quantity = qty_elem[0].value;
                total_amount_elem[0].value = quantity * price;
            }

            function compute_minmax_quantity() {
                var price = amount_elem[0]
                    .options[amount_elem.prop("selectedIndex")]
                    .dataset
                    .price;
                var min_amount = amount_elem[0]
                    .options[amount_elem.prop("selectedIndex")]
                    .dataset
                    .min_amount;
                var max_amount = amount_elem[0]
                    .options[amount_elem.prop("selectedIndex")]
                    .dataset
                    .max_amount;
                if (min_amount) {
                    var min_qty = Math.ceil(min_amount / price);
                    qty_elem.attr("min", min_qty);
                } else {
                    qty_elem.attr("min", 1);
                }
                if (max_amount >= 0) {
                    var max_qty = Math.floor(max_amount / price);
                    qty_elem.attr("max", max_qty);
                } else {
                    qty_elem.removeAttr("max");
                }
            }

            amount_elem.change(function() {
                compute_total_amount();
                compute_minmax_quantity();
            });
            qty_elem.change(compute_total_amount);
            compute_total_amount();
            compute_minmax_quantity();
        });
    });

});
