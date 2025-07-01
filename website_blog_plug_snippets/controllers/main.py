# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug
import itertools
import pytz
import babel.dates
from collections import OrderedDict

from odoo import http, fields
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.http import request
from odoo.osv import expression


class AppWebsiteBlog(WebsiteBlog):

    @http.route(['/blog/render_plug_posts'], type='json', auth='public', website=True)
    def render_plug_posts(self, template, domain, limit=None, order='plug_sequence asc'):
        dom = expression.AND([
            [('website_published', '=', True), ('post_date', '<=', fields.Datetime.now()), ('is_plug', '=', True)],
            request.website.website_domain()
        ])
        if domain:
            dom = expression.AND([dom, domain])
        posts = request.env['blog.post'].search(dom, limit=limit, order=order)
        return request.website.viewref(template)._render({'posts': posts})
