# Copyright 2019 Coop IT Easy SCRLfs <http://coopiteasy.be>
#   - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""Auth Sign up Form"""

from collections import OrderedDict
from datetime import date

from odoo import tools
from odoo.addons.base_iban.models import res_partner_bank
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.translate import _

from .form import Choice, Field, Form, FormValidationError


class SignupForm(Form):
    """Form to signup with minimal information"""

    def add_fields(self):
        self.fields["login"] = Field(
            label="E-mail",
            required=True,
            att={"autofocus": "autofocus", "autocapitalize": "off"},
            validators=[self._validate_login],
            template="iwp_website.input_field",
            input_type="email",
        )
        self.fields["confirm_login"] = Field(
            label="Confirm E-mail",
            required=True,
            att={"autocapitalize": "off"},
            template="iwp_website.input_field",
            input_type="email",
        )
        self.fields["password"] = Field(
            label="Password",
            required=True,
            validators=[self._validate_password],
            template="iwp_website.input_field",
            input_type="password",
        )
        self.fields["confirm_password"] = Field(
            label="Confirm Password",
            required=True,
            template="iwp_website.input_field",
            input_type="password",
        )
        if (
            request.env["res.company"]
            ._company_default_get()
            .data_policy_approval_required
        ):
            self.fields["data_policy_approval"] = Field(
                label="Accept Data Policy",
                required=True,
                template="iwp_website.checkbox_field",
            )

    def clean(self):
        """Validate that confirmation field are correctly filled in."""
        cleaned_data = super().clean()
        # Login and confirmation
        if cleaned_data.get("login") != cleaned_data.get("confirm_login"):
            raise FormValidationError(
                _("The email and confirmation email must be the same.")
            )
        # Password and confirmation
        if cleaned_data.get("password") != cleaned_data.get(
            "confirm_password"
        ):
            raise FormValidationError(
                _("The password and confirmation password does not match.")
            )
        return cleaned_data

    def _validate_login(self, value):
        """Validate login. Raise Error if validation doesn't succeed."""
        if not tools.single_email_re.match(value):
            raise FormValidationError(
                _("That does not seem to be an email address.")
            )

    def _validate_password(self, value):
        """Validate password. Raise Error if validation doesn't succeed."""
        if len(value) < 8:
            raise FormValidationError(
                _("Password must be at least 8 characters long.")
            )


class AddressForm(Form):
    """Form to get an address."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "street"] = Field(
            label="Address",
            required=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "zip_code"] = Field(
            label="Zip / Postal Code",
            required=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "city"] = Field(
            label="City",
            required=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "country"] = Field(
            label="Country",
            required=True,
            template="iwp_website.selection_field",
            choices=self._choices_country,
        )

    def _choices_country(self):
        countries = request.env["res.country"].sudo().search([])
        choices = []
        for country in countries:
            choices.append(
                Choice(
                    value=str(country.id), display=country.name, obj=country
                )
            )
        return choices


class BankAccountForm(Form):
    """Form to get an bank account number."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "bank_account"] = Field(
            label="Bank Account Number",
            required=True,
            validators=[self._validate_bank_account],
            template="iwp_website.input_field",
            input_type="text",
        )

    def _validate_bank_account(self, value):
        try:
            res_partner_bank.validate_iban(value)
        except ValidationError:
            raise FormValidationError(_("Please give a correct IBAN number."))


class LanguageForm(Form):
    """Form to get the language of a user."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "lang"] = Field(
            label="Language",
            required=True,
            template="iwp_website.selection_field",
            choices=self._choices_lang,
        )

    def _choices_lang(self):
        langs = request.env["res.lang"].sudo().search([])
        choices = []
        for lang in langs:
            choices.append(
                Choice(value=str(lang.code), display=lang.name, obj=lang)
            )
        return choices


class PersonForm(Form):
    """Form to edit information about an person."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "firstname"] = Field(
            label="Firstname",
            required=True,
            att={"autofocus": "autofocus"},
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "lastname"] = Field(
            label="Lastname",
            required=True,
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "gender"] = Field(
            label="Gender",
            required=True,
            template="iwp_website.selection_field",
            choices=self._choices_gender,
        )
        self.fields[prefix + "birthdate"] = Field(
            label="Birthdate",
            required=True,
            att={"max": date.today().isoformat()},
            validators=[self._validate_birthdate],
            template="iwp_website.input_field",
            input_type="date",
        )
        self.fields[prefix + "phone"] = Field(
            label="Phone",
            required=True,
            template="iwp_website.input_field",
            input_type="tel",
        )

    def _validate_birthdate(self, value, field):
        """Validate birthdate. Raise Error if validation doesn't succeed."""
        maximum = field.att.get("max")
        if maximum and value > field.to_python(maximum):
            raise FormValidationError(_("Bithdate must be in the past."))

    def _choices_gender(self):
        sub_req_mgr = request.env["subscription.request"]
        gender_field = sub_req_mgr.sudo().fields_get(["gender"])["gender"]
        choices = []
        for gender in gender_field["selection"]:
            choices.append(
                Choice(value=str(gender[0]), display=gender[1], obj=gender)
            )
        return choices


class CompanyForm(Form):
    """Form to edit information about an company."""

    def add_fields(self, prefix=""):
        self.fields[prefix + "name"] = Field(
            label="Company Name",
            required=True,
            att={"autofocus": "autofocus"},
            template="iwp_website.input_field",
            input_type="text",
        )
        self.fields[prefix + "phone"] = Field(
            label="Phone",
            required=True,
            template="iwp_website.input_field",
            input_type="tel",
        )


class InvestorPersonForm(
    PersonForm, BankAccountForm, LanguageForm, AddressForm
):
    """Form to edit informations about a investor."""

    def __init__(self, add_fields=True, **kwargs):
        super().__init__(**kwargs)
        if add_fields:
            self.add_fields()

    def add_fields(self):
        PersonForm.add_fields(self)
        BankAccountForm.add_fields(self)
        LanguageForm.add_fields(self)
        AddressForm.add_fields(self)


class InvestorCompanyForm(
    CompanyForm, BankAccountForm, LanguageForm, AddressForm, PersonForm
):
    """Form to edit informations about a company investor."""

    def __init__(self, add_fields=True, **kwargs):
        super().__init__(**kwargs)
        if add_fields:
            self.add_fields()

    def add_fields(self):
        CompanyForm.add_fields(self)
        BankAccountForm.add_fields(self)
        LanguageForm.add_fields(self)
        AddressForm.add_fields(self)
        PersonForm.add_fields(self, prefix="rep_")
        AddressForm.add_fields(self, prefix="rep_")


class InvestorPersonSignupForm(SignupForm, InvestorPersonForm):
    """Form to register informations about a investor."""

    def __init__(self, **kwargs):
        super().__init__(add_fields=False, **kwargs)
        self.add_fields()

    def add_fields(self):
        SignupForm.add_fields(self)
        InvestorPersonForm.add_fields(self)


class InvestorCompanySignupForm(SignupForm, InvestorCompanyForm):
    """Form to register informations about a company investor."""

    def __init__(self, **kwargs):
        super().__init__(add_fields=False, **kwargs)
        self.add_fields()

    def add_fields(self):
        SignupForm.add_fields(self)
        InvestorCompanyForm.add_fields(self)
