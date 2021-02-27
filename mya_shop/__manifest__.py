# -*- coding: utf-8 -*-
{
    'name': "mya_shop",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Mia cosmétique fashion shop
    """,

    'author': "Abdou Mbar Ly",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','sale','hr','point_of_sale','stock','mail'],

    # always loaded
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/ir_sequence.xml',
        'report/demande_appro_template.xml',
        'report/convention_fiche_traitement.xml',
        'report/report.xml',
        'data/mail_template.xml',
        'data/prestation_type.xml',
        #'data/produits.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}