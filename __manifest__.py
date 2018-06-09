# -*- coding: utf-8 -*-
{
    'name': "Sama Discount",
    'summary': """Remise dans les rapports""",
    'description': """
        Permet d'ajouter une remise globale sur le devis ou la facture
    """,
    'author': "Xayma Solutions",
    'website': "http://www.xayma-solutions.com",
    'category': 'Sales Management',
    'version': '11.0.0.1',
    'depends': ['base','sale_management'],
    'data': [
        'views/saleorder.form.samarem.xml',
        'views/invoice.doc.samarem.xml',
    ],
    'demo': [],
}