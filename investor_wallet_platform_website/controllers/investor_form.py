# Copyright 2019-     Coop IT Easy SCRLfs <http://coopiteasy.be>
#     - Rémy Taymans <remy@coopiteasy.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import tools
from odoo.addons.base_iban.models import res_partner_bank
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.tools.translate import _


class InvestorForm():

    @staticmethod
    def validate_form(qcontext=None):
        """
        Populate request.parms with errors if the params from the form
        are not correct. If a qcontext is given, this function works on
        this qcontext.
        """
        if not qcontext:
            qcontext = request.params
        if qcontext.get('iban', False):
            try:
                res_partner_bank.validate_iban(qcontext.get("iban"))
            except ValidationError:
                qcontext['error'] = _("Please give a correct IBAN number.")
        return qcontext

    @staticmethod
    def init_form_data(qcontext=None):
        """
        Populate qcontext if given, else populate request.params with
        generic data needed to render the form. See also
        set_form_defaults to set default value to each fields of the form.
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

    @staticmethod
    def set_form_defaults(qcontext=None, force=False):
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

    @staticmethod
    def normalize_form_data(qcontext=None):
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


class InvestorCompanyForm(InvestorForm):

    @staticmethod
    def validate_form(qcontext=None):
        """
        Populate request.parms with errors if the params from the form
        are not correct. If a qcontext is given, this function works on
        this qcontext.
        """
        if not qcontext:
            qcontext = request.params
        qcontext = InvestorForm.validate_form(qcontext=qcontext)
        return qcontext

    @staticmethod
    def init_form_data(qcontext=None):
        """
        Populate qcontext if given, else populate request.params with
        generic data needed to render the form. See also
        set_form_defaults to set default value to each fields of the form.
        """
        if not qcontext:
            qcontext = request.params
        qcontext = InvestorForm.init_form_data(qcontext=qcontext)
        return qcontext

    @staticmethod
    def set_form_defaults(qcontext=None, force=False):
        """
        Populate the given qcontext or request.parms if empty with the
        default value for the form.
        """
        if not qcontext:
            qcontext = request.params
        qcontext = InvestorForm.set_form_defaults(qcontext=qcontext)
        if 'rep_country_id' not in qcontext or force:
            qcontext['rep_country_id'] = (request.env['res.country'].sudo()
                                          .search([('code', '=', 'BE')]).id)
        if 'rep_gender' not in qcontext or force:
            qcontext['rep_gender'] = 'other'
        return qcontext

    @staticmethod
    def normalize_form_data(qcontext=None):
        """
        Normalize data encoded by the user.
        """
        if not qcontext:
            qcontext = request.params
        qcontext = InvestorForm.normalize_form_data(qcontext=qcontext)
        # The keyword zip is overwrite in the template by the zip
        # standard class of python. So we converted it into 'zip_code'
        # As this happens only in template, we can continue to use 'zip'
        # in the controller.
        if 'rep_zip_code' in qcontext:
            qcontext['rep_zip'] = qcontext['rep_zip_code']
        if 'rep_country_id' in qcontext:
            qcontext['rep_country_id'] = int(qcontext['rep_country_id'])
        return qcontext


class SignupForm():

    @staticmethod
    def validate_form(qcontext=None):
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
        return qcontext

    @staticmethod
    def init_form_data(qcontext=None):
        """
        Populate qcontext if given, else populate request.params with
        generic data needed to render the form. See also
        set_form_defaults to set default value to each fields of the form.
        """
        return qcontext

    @staticmethod
    def set_form_defaults(qcontext=None, force=False):
        """
        Populate the given qcontext or request.parms if empty with the
        default value for the form.
        """
        if not qcontext:
            qcontext = request.params
        return qcontext

    @staticmethod
    def normalize_form_data(qcontext=None):
        """
        Normalize data encoded by the user.
        """
        return qcontext


class InvestorSignupForm(InvestorForm, SignupForm):

    @staticmethod
    def validate_form(qcontext=None):
        qcontext = InvestorForm.validate_form(qcontext=qcontext)
        qcontext = SignupForm.validate_form(qcontext=qcontext)
        return qcontext

    @staticmethod
    def init_form_data(qcontext=None):
        """
        Populate qcontext if given, else populate request.params with
        generic data needed to render the form. See also
        set_form_defaults to set default value to each fields of the form.
        """
        qcontext = InvestorForm.init_form_data(qcontext=qcontext)
        qcontext = SignupForm.init_form_data(qcontext=qcontext)
        return qcontext

    @staticmethod
    def set_form_defaults(qcontext=None, force=False):
        """
        Populate the given qcontext or request.parms if empty with the
        default value for the form.
        """
        qcontext = InvestorForm.set_form_defaults(qcontext=qcontext)
        qcontext = SignupForm.set_form_defaults(qcontext=qcontext)
        return qcontext

    @staticmethod
    def normalize_form_data(qcontext=None):
        """
        Normalize data encoded by the user.
        """
        qcontext = InvestorForm.normalize_form_data(qcontext=qcontext)
        qcontext = SignupForm.normalize_form_data(qcontext=qcontext)
        return qcontext


class InvestorCompanySignupForm(InvestorCompanyForm, SignupForm):

    @staticmethod
    def validate_form(qcontext=None):
        qcontext = InvestorCompanyForm.validate_form(qcontext=qcontext)
        qcontext = SignupForm.validate_form(qcontext=qcontext)
        return qcontext

    @staticmethod
    def init_form_data(qcontext=None):
        """
        Populate qcontext if given, else populate request.params with
        generic data needed to render the form. See also
        set_form_defaults to set default value to each fields of the form.
        """
        qcontext = InvestorCompanyForm.init_form_data(qcontext=qcontext)
        qcontext = SignupForm.init_form_data(qcontext=qcontext)
        return qcontext

    @staticmethod
    def set_form_defaults(qcontext=None, force=False):
        """
        Populate the given qcontext or request.parms if empty with the
        default value for the form.
        """
        qcontext = InvestorCompanyForm.set_form_defaults(qcontext=qcontext)
        qcontext = SignupForm.set_form_defaults(qcontext=qcontext)
        return qcontext

    @staticmethod
    def normalize_form_data(qcontext=None):
        """
        Normalize data encoded by the user.
        """
        qcontext = InvestorCompanyForm.normalize_form_data(qcontext=qcontext)
        qcontext = SignupForm.normalize_form_data(qcontext=qcontext)
        return qcontext
