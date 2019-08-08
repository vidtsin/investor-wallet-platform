# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo import tools
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_partner import SignupError
from odoo.addons.base_iban.models import res_partner_bank
from odoo.addons.investor_wallet_platform_website.controllers.investor_form import InvestorSignupForm
from odoo.addons.investor_wallet_platform_website.controllers.investor_form import InvestorCompanySignupForm
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.translate import _



class AuthSignupInvestor(AuthSignupHome):

    @http.route(['/web/signup', '/web/investor/signup'])
    def web_auth_signup(self, *args, **kw):
        """Signup for a investor (individual)"""
        form = InvestorSignupForm()
        # Prepare the form
        form.normalize_form_data(request.params)
        form.validate_form(request.params)
        form.init_form_data(request.params)
        form.set_form_defaults(request.params)
        if 'firstname' in request.params or 'lastname' in request.params:
            request.params['name'] = form.generate_name_field(
                request.params.get('firstname', ''),
                request.params.get('lastname', ''),
            )
        # Process the form
        response = super().web_auth_signup(*args, **kw)
        res_qcontext = response.qcontext
        if ('error' not in res_qcontext
                and request.httprequest.method == 'POST'):
            # Finish filling special fields
            n_user = None
            if 'login' in request.params:
                n_user = (request.env['res.users']
                          .search([('login', '=', request.params['login'])]))
            if not n_user:
                res_qcontext['error'] = _("The new user cannot be found.")
            else:
                values = {key: request.params[key]
                          for key in request.params
                          if key in self.get_user_fields()}
                n_user.sudo().write(values)
                request.env['res.partner.bank'].sudo().create({
                    'partner_id': n_user.partner_id.id,
                    'acc_number': request.params['iban'],
                })
                request.cr.commit()
        # Render the response
        if response.template == 'auth_signup.signup':
            return request.render(
                'investor_wallet_platform_website.signup_investor',
                res_qcontext
            )
        return response

    @staticmethod
    def get_user_fields():
        """
        Return names of the fields of a res_user object that are in the
        form.  It does not return fields that are already used in the
        `do_signup()` method from parent class.
        """
        return [
            'firstname',
            'lastname',
            'gender',
            'phone',
            'street',
            'city',
            'zip',
            'country_id',
            'lang',
        ]

    @staticmethod
    def get_company_fields():
        """
        Return names of the fields of a res_user object that are in the
        form.  It does not return fields that are already used in the
        `do_signup()` method from parent class.
        """
        return [
            'phone',
            'street',
            'city',
            'zip',
            'country_id',
            'lang',
        ]

    @staticmethod
    def get_representative_fields():
        """
        Return names of the fields of a res_user object that are in the
        form.  It does not return fields that are already used in the
        `do_signup()` method from parent class.
        """
        return [
            'rep_firstname',
            'rep_lastname',
            'rep_function',
            'rep_gender',
            'rep_phone',
            'rep_street',
            'rep_city',
            'rep_zip',
            'rep_country_id',
        ]

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
