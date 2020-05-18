# Copyright 2019-2020 Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import http, tools
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_partner import SignupError
from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools.translate import _

from .form import FormError
from .auth_signup_form import (InvestorCompanySignupForm,
                               InvestorPersonSignupForm)

_logger = logging.getLogger(__name__)


class AuthSignupInvestor(AuthSignupHome):

    @http.route(['/web/signup', '/web/investor/signup'])
    def web_auth_signup(self, *args, **kw):
        """Signup for a investor (individual)"""
        qcontext = self.get_auth_signup_qcontext()
        form_context = {}
        if request.httprequest.method == "POST":
            form = self.investor_signup_form(data=request.params)
            try:
                form.full_clean()
            except FormError as err:
                form.add_error("__all__", err)
                _logger.error(err)
            if "error" in qcontext:
                form.add_error("__all__", qcontext["error"])
            if form.is_valid():
                form_context["token"] = qcontext.get("token")
                try:
                    self.process_investor_signup_form(
                        form, context=form_context
                    )
                except (UserError, SignupError, ValidationError) as err:
                    form.add_error("__all__", err)
                    _logger.error(err)
                else:
                    return self.web_login(*args, **kw)
        else:
            form = self.investor_signup_form()
        qcontext.update({"form": form})
        return request.render("iwp_website.investor_signup_form", qcontext)

    def investor_signup_form(self, data=None, context=None):
        """Return form object."""
        form = InvestorPersonSignupForm(
            initial=self.investor_signup_form_initial(context=context),
            data=data or None,
            context=context,
        )
        return form

    def investor_signup_form_initial(self, context=None):
        """Return initials for investor form."""
        context = {} if context is None else context
        initial = {}
        initial["country"] = str(
            request.env['res.company']._company_default_get().country_id.id
        )
        initial["gender"] = 'other'
        initial["lang"] = request.lang
        return initial

    def process_investor_signup_form(self, form, context=None):
        """Process the signup with creation of the new user and partner"""
        self._signup_with_values(
            context.get('token'), self.investor_vals(form)
        )
        request.env.cr.commit()

    def investor_vals(self, form, context=None):
        """Return vals to add information on a res.users."""
        vals = {
            "login": form.cleaned_data["login"],
            "password": form.cleaned_data["password"],
            "firstname": form.cleaned_data["firstname"],
            "lastname": form.cleaned_data["lastname"],
            "name": "{} {}".format(
                form.cleaned_data["firstname"],
                form.cleaned_data["lastname"],
            ),
            "gender": form.cleaned_data["gender"],
            "phone": form.cleaned_data["phone"],
            "birthdate_date": form.cleaned_data["birthdate"],
            "street": form.cleaned_data["street"],
            "city": form.cleaned_data["city"],
            "zip": form.cleaned_data["zip_code"],
            "country_id": form.cleaned_data["country"],
            "lang": form.cleaned_data["lang"],
            "bank_ids": [
                (0, None, {"acc_number": form.cleaned_data["bank_account"]})
            ],
        }
        return vals

    @http.route(
        '/web/investor/company/signup',
        type='http',
        auth='public',
        website=True,
        sitemap=False
    )
    def web_auth_signup_investor_company(self, *args, **kw):
        """Signup for an investor company"""
        qcontext = self.get_auth_signup_qcontext()
        form_context = {}
        if request.httprequest.method == "POST":
            form = self.company_signup_form(data=request.params)
            try:
                form.full_clean()
            except FormError as err:
                form.add_error("__all__", err)
                _logger.error(err)
            if "error" in qcontext:
                form.add_error("__all__", qcontext["error"])
            if form.is_valid():
                form_context["token"] = qcontext.get("token")
                try:
                    self.process_company_signup_form(
                        form, context=form_context
                    )
                except (UserError, SignupError, ValidationError) as err:
                    form.add_error("__all__", err)
                    _logger.error(err)
                else:
                    return self.web_login(*args, **kw)
        else:
            form = self.company_signup_form()
        qcontext.update({"form": form})
        return request.render("iwp_website.company_signup_form", qcontext)

    def company_signup_form(self, data=None, context=None):
        """Return form object."""
        form = InvestorCompanySignupForm(
            initial=self.company_signup_form_initial(context=context),
            data=data or None,
            context=context,
        )
        return form

    def company_signup_form_initial(self, context=None):
        """Return initials for a company investor form."""
        context = {} if context is None else context
        initial = {}
        initial["country"] = str(
            request.env['res.company']._company_default_get().country_id.id
        )
        initial["rep_country"] = initial["country"]
        initial["rep_gender"] = 'other'
        initial["lang"] = request.lang
        return initial

    def process_company_signup_form(self, form, context=None):
        """Process the signup with creation of the new user and partner"""
        try:
            company = request.env["res.partner"].sudo().create(
                self.company_vals(form, context=context)
            )
        except Exception as err:
            _logger.error(err)
            raise SignupError(_("Can not create company."))
        context["company"] = company
        try:
            self._signup_with_values(
                context.get("token"),
                self.representative_vals(form, context=context)
            )
        except Exception as err:
            _logger.error(err)
            company.unlink()
            raise SignupError(_("Can not create user."))

    def company_vals(self, form, context=None):
        """Return vals to create company res.users."""
        vals = {
            "company_type": "company",
            "name": form.cleaned_data["name"],
            "email": form.cleaned_data["login"],
            "phone": form.cleaned_data["phone"],
            "street": form.cleaned_data["street"],
            "city": form.cleaned_data["city"],
            "zip": form.cleaned_data["zip_code"],
            "country_id": form.cleaned_data["country"],
            "bank_ids": [
                (0, 0, {"acc_number": form.cleaned_data["bank_account"]})
            ],
        }
        return vals

    def representative_vals(self, form, context=None):
        """
        Return vals to create a representative for a company res.users.
        """
        context = {} if context is None else context
        vals = {
            "type": 'representative',
            "company_type": "person",
            "representative": True,
            "login": form.cleaned_data["login"],
            "password": form.cleaned_data["password"],
            "firstname": form.cleaned_data["rep_firstname"],
            "lastname": form.cleaned_data["rep_lastname"],
            "name": "{} {}".format(
                form.cleaned_data["rep_firstname"],
                form.cleaned_data["rep_lastname"],
            ),
            "email": form.cleaned_data["login"],
            "gender": form.cleaned_data["rep_gender"],
            "phone": form.cleaned_data["rep_phone"],
            "birthdate_date": form.cleaned_data["rep_birthdate"],
            "street": form.cleaned_data["rep_street"],
            "city": form.cleaned_data["rep_city"],
            "zip": form.cleaned_data["rep_zip_code"],
            "country_id": form.cleaned_data["rep_country"],
            "lang": form.cleaned_data["lang"],
        }
        if "company" in context:
            vals["parent_id"] = context["company"].id
        return vals

    def get_auth_signup_qcontext(self):
        """Add data policy approval"""
        qcontext = super().get_auth_signup_qcontext()
        qcontext["data_policy_text"] = (
            request.env["res.company"]
            ._company_default_get()
            .data_policy_approval_text
        )
        return qcontext

    def get_auth_signup_config(self):
        """
        Overwrite the signup config from parent to take the
        configuration for investor sign up in place of the default
        authentication.
        """
        conf = super().get_auth_signup_config()
        get_param = request.env['ir.config_parameter'].sudo().get_param
        conf['signup_enabled'] = (
            get_param('investor_wallet_platform.investor_signup_enabled', True)
            and conf['signup_enabled']
        )
        return conf
