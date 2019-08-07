# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo import tools
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_partner import SignupError
from odoo.addons.base_iban.models import res_partner_bank
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.translate import _


class AuthSignupInvestor(AuthSignupHome):

    @http.route(['/web/signup', '/web/investor/signup'])
    def web_auth_signup(self, *args, **kw):
        # Prepare the form
        self.normalize_form_data()
        self.validate_form()
        self.init_form_data()
        self.set_form_defaults()
        if 'firstname' in request.params or 'lastname' in request.params:
            request.params['name'] = self.generate_name_field(
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

    def validate_form(self, qcontext=None):
        """
        Populate request.parms with errors if the params from the form
        are not correct. If a qcontext is given, this function works on
        this qcontext.
        """
        if not qcontext:
            qcontext = request.params
        if qcontext.get('login', False):
            if not tools.single_email_re.match(qcontext.get('login', '')):
                qcontext['error'] = _("That does not seem to be an email"
                                      " address.")
        if qcontext.get('login') != qcontext.get('confirm_login'):
            qcontext['error'] = _(
                "The email and confirmation email must be the same."
            )
        if qcontext.get('iban', False):
            try:
                res_partner_bank.validate_iban(qcontext.get("iban"))
            except ValidationError:
                qcontext['error'] = _("Please give a correct IBAN number.")
        return qcontext

    def init_form_data(self, qcontext=None):
        """
        Populate qcontext if given, else populate request.params with
        defalut data needed to render the form.
        """
        if not qcontext:
            qcontext = request.params
        sub_req_mgr = request.env['subscription.request']
        gender_field = sub_req_mgr.sudo().fields_get(['gender'])['gender']
        qcontext.update({
            'genders': gender_field['selection'],
            'countries': request.env['res.country'].sudo().search([]),
            'langs': request.env['res.lang'].sudo().search([]),
        })
        return qcontext

    def set_form_defaults(self, qcontext=None, force=False):
        """
        Populate the given qcontext or request.parms if empty with the
        default value for the form.
        """
        if not qcontext:
            qcontext = request.params
        if 'country_id' not in qcontext or force:
            qcontext['country_id'] = (request.env['res.country'].sudo()
                                      .search([('code', '=', 'BE')]).id)
        if 'gender' not in qcontext or force:
            qcontext['gender'] = 'other'
        if 'lang' not in qcontext or force:
            lang_mgr = request.env['res.lang']
            supported_langs = [
                lang['code']
                for lang in lang_mgr.sudo().search_read([], ['code'])
            ]
            if request.lang in supported_langs:
                qcontext['lang'] = request.lang
        return qcontext

    def normalize_form_data(self, qcontext=None):
        """
        Normalize data encoded by the user.
        """
        if not qcontext:
            qcontext = request.params
        # The keyword zip is overwrite in the template by the zip
        # standard class of python. So we converted it into 'zip_code'
        # As this happens only in template, we can continue to use 'zip'
        # in the controller.
        if 'zip_code' in qcontext:
            qcontext['zip'] = qcontext['zip_code']
        # Strip all str values
        for key, val in qcontext.items():
            if isinstance(val, str):
                qcontext[key] = val.strip()
        # Convert to int when needed
        if 'country_id' in qcontext:
            qcontext['country_id'] = int(qcontext['country_id'])
        return qcontext

    @staticmethod
    def generate_name_field(firstname, lastname):
        """
        Generate a name based on firstname and lastname.
        """
        return ("%s %s" % (firstname, lastname)).strip()

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
