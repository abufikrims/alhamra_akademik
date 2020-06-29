# -*- coding: utf-8 -*-
{
    'name': "alhamra_akademik",

    'summary': """
        Sistem Informasi Akademik 
        Islamic Boarding School Alhamra""",

    'description': """
        Sistem Informasi Akademik ini dikembangkan secara modular, terdiri dari
        alhamra_akademik
        alhamra_kesantrian
        
    """,

    'author': "Cendana2000",
    'website': "http://www.cendana2000.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Education',
    'version': '12.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail', 'hr', 'aa_account_period', 'calendar', 'account', 'account_voucher', 'account_cancel', 'sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/wizard_view.xml',
        'views/master_kelas.xml',
        'views/ruang_kelas.xml',
        'views/matapelajaran.xml',
        'views/siswa.xml',
        'views/orangtua.xml',
        'views/orangtua_view.xml',
        'views/guru.xml',
        'views/tatausaha.xml',
        'views/invoice_view.xml',
        'views/uangsaku.xml',
        'views/jadwal_pelajaran.xml',
        'views/kalender_akademik.xml',
        'views/penilaian.xml',
        'views/menu.xml',

    ],
    'images': [],
    'license': 'AGPL-3',
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}