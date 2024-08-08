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
    'name': 'Website Blog: Blog Instagram',
    'version': '16.0.0.0.0',
    'summary': 'Fetch instagram posts and post back to instagram.',
    'category': 'Website',
    'description': """
        Makes it easy to fetch instagram posts and post back to instagram.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-website-blog/blog_instagram',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-website-blog',
    'depends': ['website_blog'],
    'data': [
        'data/data.xml',
        'views/blog_post_view.xml',
    ],
    'external_dependencies': {
        'python': ['ensta']
    },
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4s:softtabstop=4:shiftwidth=4:
