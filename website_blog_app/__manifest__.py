# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2022- Vertel AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Website Blog: Website Blog App',
    'version': '18.0.0.0.1',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Website Blog App',
    'category': 'Website',
    'description': """
    Website Blog App
    """,
    #'sequence': '200',
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-website-blog/website_blog_app',
    'images': ['/static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-website-blog',
    'depends': ['website_blog'],
    'data': [
	    'security/ir.model.access.csv',
        'views/snippets/snippets.xml',
        'views/website_blog_view.xml',
        'views/website_blog_templates.xml',
        'views/app_templates.xml',
        # 'views/assets.xml',
        'data/ir_config_parameter.xml',
        'data/server_action.xml',
        'data/data.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_blog_app/static/scss/snippet_styles.scss',
            'website_blog_app/static/css/tooltip_style.css'
        ]
    },
    'installable': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
