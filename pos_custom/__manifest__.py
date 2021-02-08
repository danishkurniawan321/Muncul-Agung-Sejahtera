# -*- coding: utf-8 -*-
{
    'name': "Custom POS v14",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "dodyakj",
    # 'website': "http://www.yourcompany.com",
    'category': 'pos',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','point_of_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/Screens/ProductScreen/NumpadWidget.xml',
       ],
    "sequence": 0,
    "application": True,
    "installable": True,
    "auto_install": False,

}
