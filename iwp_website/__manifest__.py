# Copyright 2019 Coop IT Easy SCRLfs
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Investor Wallet Platform Website",
    'summary': """
        Website element for Investor Wallet Platform""",
    'version': '12.0.0.8.0',
    'license': 'AGPL-3',
    'author': "Coop IT Easy SCRLfs",
    'website': "https://coopiteasy.be",
    'depends': [
        'auth_signup',
        'portal',
        'investor_wallet_platform_base',
    ],
    'data': [
        'templates/auth_signup_investor.xml',
        'templates/portal_my_wallet.xml',
        'templates/investor_portal.xml',
        'templates/investor_form.xml',
        'templates/subscription_request.xml',
    ],
}
