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
    });

});
