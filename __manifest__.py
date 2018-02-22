# -*- coding: utf-8 -*-
{
    'name': "Sama Remise Globale",

    'summary': """
        Remise globale""",

    'description': """
        Permet d'ajouter une remise globale sur le devis ou la facture
    """,

    'author': "Elhadji Malang Diedhiou",
    'website': "http://www.supermalang.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '11.0',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}