# -*- coding: utf-8 -*-
{
    'name': "Arknana Report 13",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "dodyakj",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','sale_management','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reports/report.xml',
        'reports/report_stockpicking_operations.xml',
        'reports/report_deliveryslip.xml',
    ],
    # only loaded in demonstration mode
    "sequence": 0,
    "application": True,
    "installable": True,
    "auto_install": False,
}
