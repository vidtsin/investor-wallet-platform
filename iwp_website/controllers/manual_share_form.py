# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Manual Share Form"""

from collections import OrderedDict
from datetime import date

from odoo.http import request

from .form import Field, Form, FormValidationError


class ManualShareForm(Form):
    """Form to create new Manual Share for a user"""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.fields = OrderedDict()
        self.fields["share_type"] = Field(
            label="Share Type",
            required=True,
            validators=[self._validate_share_type],
            template="iwp_website.selection_field",
            choices=self._choices_share_type,
        )
        self.fields["quantity"] = Field(
            label="Quantity",
            required=True,
            att={"min": 1},
            validators=[self._validate_quantity],
            template="iwp_website.input_field",
            input_type="number",
        )
        self.fields["total_amount"] = Field(
            label="Total Amount",
            readonly=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields["date"] = Field(
            label="Date",
            required=True,
            att={"max": date.today().isoformat()},
            validators=[self._validate_date],
            template="iwp_website.input_field",
            input_type="date",
        )

    def _validate_share_type(self, value):
        """
        Validate share_type. Raise Error if validation doesn't succeed.
        """
        share_types_ids = [
            st["value"] for st in self.fields["share_type"].choices()
        ]
        # Check share type are in the choices
        if value not in share_types_ids:
            raise FormValidationError(
                "The selected share is not valid choice."
            )

    def _validate_quantity(self, value):
        minimum = self.fields["quantity"].att.get("min")
        if minimum and value < minimum:
            raise FormValidationError("Minimun %d." % minimum)

    def _validate_date(self, value):
        maximum = self.fields["date"].att.get("max")
        if maximum and value > date.fromisoformat(maximum):
            raise FormValidationError("Please enter date in the past.")

    def _choices_share_type(self):
        user = self.context.get("user")
        struct = self.context.get("struct")
        if user.is_company:
            share_types = struct.share_type_ids.filtered(
                lambda r: r.display_on_website and r.by_company
            )
        else:
            share_types = struct.share_type_ids.filtered(
                lambda r: r.display_on_website and r.by_individual
            )
        # TODO: choices should be a list of choices object.
        choices = []
        if struct:
            for st in share_types:
                choices.append(
                    {
                        "value": str(st.id),
                        "display": "%s - %s" % (st.name, st.list_price),
                        "att": {"data-amount": st.list_price},
                        "obj": st,
                    }
                )
        return choices
