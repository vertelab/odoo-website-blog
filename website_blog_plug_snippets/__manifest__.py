# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2021- Vertel AB (<https://vertel.se>).
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
    'name': 'Website Blog: App Snippets',
    'version': '18.0.0.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'summary': 'Website Blog App',
    'category': 'Website',
    'description': """
    """,
    #'sequence': '1'
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-website-blog/website_blog_plug_snippets',
    'images': ['/static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-website-blog',
    'depends': ['website_blog', 'web_editor'],
    'data': [
        'views/website_blog_view.xml',
        'views/snippets/snippets.xml',
        'views/snippets/snip_plug_posts.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_blog_plug_snippets/static/src/snippets/snip_plug_posts/plug_posts.scss',
            'website_blog_plug_snippets/static/src/snippets/snip_plug_posts/plug_posts_001.scss',
        ],
        'website_blog_plug_snippets.assets_wysiwyg': [
            'website_blog_plug_snippets/static/src/snippets/snip_plug_posts/plug_posts.js'
        ]
    },
    'installable': True,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

