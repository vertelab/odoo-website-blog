# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug
import itertools
import pytz
import babel.dates
from collections import OrderedDict

from odoo import http, fields
# from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.portal.controllers.portal import _build_url_w_params
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.http import request
from odoo.osv import expression
from odoo.tools import html2plaintext
from odoo.tools.misc import get_lang
from odoo.tools import sql
import logging

_logger = logging.getLogger(__name__)

# _unslug = request.env['ir.http']._unslug
# slug = request.env['ir.http']._slug

class AppWebsiteBlog(WebsiteBlog):

    @http.route([
        '''/apps/<string:blog_name>/<string:blog_post_name>''',
    ], type='http', auth="public", website=True, sitemap=True)
    def app_post(self, blog_name, blog_post_name, tag_id=None, page=1, enable_editor=None, **post):
        blog = request.env['blog.blog'].search([('app_project', '=', blog_name)], limit=1)
        blog_post = request.env['blog.post'].search([('app_module', '=', blog_post_name)], limit=1)
        """ Prepare all values to display the blog.

        :return dict values: values for the templates, containing 
        
         - 'blog_post': browse of the current post
         - 'blog': browse of the current blog
         - 'blogs': list of browse records of blogs
         - 'tag': current tag, if tag_id in parameters
         - 'tags': all tags, for tag-based navigation
         - 'pager': a pager on the comments
         - 'nav_list': a dict [year][month] for archives navigation
         - 'next_post': next blog post, to direct the user towards the next interesting post
        """
        if not blog.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        BlogPost = request.env['blog.post']
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        domain = request.website.website_domain()
        blogs = blog.search(domain, order="create_date, id asc")

        tag = None
        if tag_id:
            tag = request.env['blog.tag'].browse(int(tag_id))
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog_post.blog_id, tag=tag, date_begin=date_begin,
                            date_end=date_end)

        if not blog_post.blog_id.id == blog.id:
            raise werkzeug.exceptions.NotFound()

        tags = request.env['blog.tag'].search([])

        # Find next Post
        blog_post_domain = [('blog_id', '=', blog.id)]
        if not request.env.user.has_group('website.group_website_designer'):
            blog_post_domain += [('post_date', '<=', fields.Datetime.now())]

        all_post = BlogPost.search(blog_post_domain)

        if blog_post not in all_post:
            if blog_post.blog_id:
                raise werkzeug.exceptions.NotFound()
            else: #  Add redirect so that visitors does not get an error message if the blog_id does not exist.
                raise werkzeug.exceptions.NotFound()

        # should always return at least the current post
        all_post_ids = all_post.ids
        current_blog_post_index = all_post_ids.index(blog_post.id)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and BlogPost.browse(next_post_id) or False

        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'blog_post': blog_post,
            'blogs': blogs,
            'main_object': blog_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'date': date_begin,
            'blog_url': blog_url,
        }
        if blog_post.is_app:
            response = request.render("website_blog_app.is_app_blog_post_complete", values)
        else:
            response = request.render("website_blog.blog_post_complete", values)

        if blog_post.id not in request.session.get('posts_viewed', []):
            if sql.increment_field_skiplock(blog_post, 'visits'):
                if not request.session.get('posts_viewed'):
                    request.session['posts_viewed'] = []
                request.session['posts_viewed'].append(blog_post.id)
                request.session.modified = True
        return response

    @http.route([
        '''/blog/<model("blog.blog"):blog>/<model("blog.post", "[('blog_id','=',blog.id)]"):blog_post>''',
        '''/apps/<model("blog.blog"):blog>/<model("blog.post", "[('blog_id','=',blog.id)]"):blog_post>'''
    ], type='http', auth="public", website=True, sitemap=True)
    def blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        """ Prepare all values to display the blog.
        
        :return dict values: values for the templates, containing

         - 'blog_post': browse of the current post
         - 'blog': browse of the current blog
         - 'blogs': list of browse records of blogs
         - 'tag': current tag, if tag_id in parameters
         - 'tags': all tags, for tag-based navigation
         - 'pager': a pager on the comments
         - 'nav_list': a dict [year][month] for archives navigation
         - 'next_post': next blog post, to direct the user towards the next interesting post
        """
        if not blog.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        BlogPost = request.env['blog.post']
        date_begin, date_end = post.get('date_begin'), post.get('date_end')

        slug = request.env['ir.http']._slug

        domain = request.website.website_domain()
        blogs = blog.search(domain, order="create_date, id asc")

        tag = None
        if tag_id:
            tag = request.env['blog.tag'].browse(int(tag_id))
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog_post.blog_id, tag=tag, date_begin=date_begin,
                            date_end=date_end)

        if not blog_post.blog_id.id == blog.id:
            return request.redirect("/blog/%s/%s" % (slug(blog_post.blog_id), slug(blog_post)), code=301)

        tags = request.env['blog.tag'].search([])

        # Find next Post
        blog_post_domain = [('blog_id', '=', blog.id)]
        if not request.env.user.has_group('website.group_website_designer'):
            blog_post_domain += [('post_date', '<=', fields.Datetime.now())]

        all_post = BlogPost.search(blog_post_domain)

        if blog_post not in all_post:
            return request.redirect("/blog/%s" % (slug(blog_post.blog_id)))

        # should always return at least the current post
        all_post_ids = all_post.ids
        current_blog_post_index = all_post_ids.index(blog_post.id)
        nb_posts = len(all_post_ids)
        next_post_id = all_post_ids[(current_blog_post_index + 1) % nb_posts] if nb_posts > 1 else None
        next_post = next_post_id and BlogPost.browse(next_post_id) or False

        values = {
            'tags': tags,
            'tag': tag,
            'blog': blog,
            'blog_post': blog_post,
            'blogs': blogs,
            'main_object': blog_post,
            'nav_list': self.nav_list(blog),
            'enable_editor': enable_editor,
            'next_post': next_post,
            'date': date_begin,
            'blog_url': blog_url,
        }
        if blog_post.is_app:
            response = request.render("website_blog_app.is_app_blog_post_complete", values)
        else:
            response = request.render("website_blog.blog_post_complete", values)

        if blog_post.id not in request.session.get('posts_viewed', []):
            if sql.increment_fields_skiplock(blog_post, 'visits'):
                if not request.session.get('posts_viewed'):
                    request.session['posts_viewed'] = []
                request.session['posts_viewed'].append(blog_post.id)
                request.session.modified = True
        return response

    def _prepare_blog_values(self, blogs, blog=False, date_begin=False, date_end=False, tags=False, state=False, page=False, search=None, is_app=False):
        """ Prepare all values to display the blogs index page or one specific blog"""
        BlogPost = request.env['blog.post']
        BlogTag = request.env['blog.tag']

        # prepare domain
        domain = request.website.website_domain()
        order="is_published desc, post_date desc, id asc"
        if blog and blog.content:
            domain += [('blog_id', '=', blog.id), ('is_app', '=', is_app)]
        if is_app:
            order = "is_published desc, sequence asc, post_date desc, id asc"

        unslug = request.env['ir.http']._unslug
        slug = request.env['ir.http']._slug

        if date_begin and date_end:
            domain += [("post_date", ">=", date_begin), ("post_date", "<=", date_end)]
        active_tag_ids = tags and [unslug(tag)[1] for tag in tags.split(',')] or []
        active_tags = BlogTag
        if active_tag_ids:
            active_tags = BlogTag.browse(active_tag_ids).exists()
            fixed_tag_slug = ",".join(slug(t) for t in active_tags)
            if fixed_tag_slug != tags:
                new_url = request.httprequest.full_path.replace("/tag/%s" % tags, "/tag/%s" % fixed_tag_slug, 1)
                if new_url != request.httprequest.full_path:  # check that really replaced and avoid loop
                    return request.redirect(new_url, 301)
            domain += [('tag_ids', 'in', active_tags.ids)]

        if request.env.user.has_group('website.group_website_designer'):
            count_domain = domain + [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            published_count = BlogPost.search_count(count_domain)
            unpublished_count = BlogPost.search_count(domain) - published_count

            if state == "published":
                domain += [("website_published", "=", True), ("post_date", "<=", fields.Datetime.now())]
            elif state == "unpublished":
                domain += ['|', ("website_published", "=", False), ("post_date", ">", fields.Datetime.now())]
        else:
            domain += [("post_date", "<=", fields.Datetime.now())]

        use_cover = request.website.is_view_active('website_blog.opt_blog_cover_post')
        fullwidth_cover = request.website.is_view_active('website_blog.opt_blog_cover_post_fullwidth_design')

        # if blog, we show blog title, if use_cover and not fullwidth_cover we need pager + latest always
        offset = (page - 1) * self._blog_post_per_page
        first_post = BlogPost
        if not blog:
            first_post = BlogPost.search(
                domain + [('website_published', '=', True), ('is_app', '=', is_app)], order=order, limit=1
            )
            if use_cover and not fullwidth_cover:
                offset += 1

        if search:
            tags_like_search = BlogTag.search([('name', 'ilike', search)])
            domain += [
                '|', '|', '|', ('author_name', 'ilike', search), ('name', 'ilike', search),
                ('content', 'ilike', search), ('tag_ids', 'in', tags_like_search.ids)
            ]
        domain += [('is_app', '=', is_app)]
        if blog and blog.id != 1:
            domain += [('blog_id','=',blog.id)]
            # ~ _logger.error(f"{blog.id=}")
            # ~ _logger.error(f"{domain=}")
        posts = BlogPost.search(domain, offset=offset, limit=self._blog_post_per_page, order=order)
        total = BlogPost.search_count(domain)

        pager = request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=total,
            page=page,
            step=self._blog_post_per_page,
        )
        # ~ _logger.error(f"{request.httprequest.path.partition('/page/')[0]=}")

        if not blogs:
            all_tags = request.env['blog.tag']
        else:
            all_tags = blogs.all_tags(join=True) if not blog else blogs.all_tags().get(blog.id, request.env['blog.tag'])
        tag_category = sorted(all_tags.mapped('category_id'), key=lambda category: category.name.upper())
        other_tags = sorted(all_tags.filtered(lambda x: not x.category_id), key=lambda tag: tag.name.upper())

        # for performance prefetch the first post with the others
        post_ids = (first_post | posts).ids

        return {
            'date_begin': date_begin,
            'date_end': date_end,
            'first_post': first_post.with_prefetch(post_ids),
            'other_tags': other_tags,
            'tag_category': tag_category,
            'nav_list': self.nav_list(),
            'tags_list': self.tags_list,
            'pager': pager,
            'posts': posts.with_prefetch(post_ids),
            'tag': tags,
            'active_tag_ids': active_tags.ids,
            'domain': domain,
            'state_info': state and {"state": state, "published": published_count, "unpublished": unpublished_count},
            'blogs': blogs,
            'blog': blog,
            'search': search,
            'search_count': total,
        }

    @http.route([
        '/blog',
        '/blog/page/<int:page>',
        '/blog/tag/<string:tag>',
        '/blog/tag/<string:tag>/page/<int:page>',
        '''/blog/<model("blog.blog"):blog>''',
        '''/blog/<model("blog.blog"):blog>/page/<int:page>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>''',
    ], type='http', auth="public", website=True, sitemap=True)
    def blog(self, blog=None, tag=None, page=1, search=None, **opt):
        Blog = request.env['blog.blog']
        if blog and not blog.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        domain = request.website.website_domain()
        domain += [('is_app', '=', False)]
        blogs = Blog.search(domain, order="create_date asc, id asc")

        slug = request.env['ir.http']._slug

        if not blog and len(blogs) == 1:
            return werkzeug.utils.redirect('/blog/%s' % slug(blogs[0]), code=302)

        date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')

        if tag and request.httprequest.method == 'GET':
            # redirect get tag-1,tag-2 -> get tag-1
            tags = tag.split(',')
            if len(tags) > 1:
                url = QueryURL(
                    '' if blog else '/blog', ['blog', 'tag'],
                    blog=blog, tag=tags[0], date_begin=date_begin,
                    date_end=date_end, search=search
                )()
                return request.redirect(url, code=302)

        values = self._prepare_blog_values(
            blogs=blogs, blog=blog, date_begin=date_begin,
            date_end=date_end, tags=tag, state=state, page=page, search=search, is_app=False
        )

        # in case of a redirection need by `_prepare_blog_values` we follow it
        if isinstance(values, werkzeug.wrappers.Response):
            return values

        if blog:
            values['main_object'] = blog
            values['edit_in_backend'] = True
            values['blog_url'] = QueryURL(
                '', ['blog', 'tag'], blog=blog, tag=tag,
                date_begin=date_begin, date_end=date_end, search=search
            )
        else:
            values['blog_url'] = QueryURL(
                '/blog', ['tag'], date_begin=date_begin, date_end=date_end, search=search
            )
        return request.render("website_blog.blog_post_short", values)
        
    @http.route([
        '/apps',
        '/apps/page/<int:page>',
        '/apps/tag/<string:tag>',
        '/apps/tag/<string:tag>/page/<int:page>',
        '''/apps/<model("blog.blog"):blog>''',
        # ~ '''/apps/<model("blog.blog"):blog>/page/<int:page>''',
        # ~ '''/apps/<model("blog.blog"):blog>/tag/<string:tag>''',
        # ~ '''/apps/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>''',
        '''/apps/<string:blog_name>/page/<int:page>''',
        '''/apps/<string:blog_name>/tag/<string:tag>''',
        '''/apps/<string:blog_name>/tag/<string:tag>/page/<int:page>''',
        '''/apps/<string:blog_name>''',
    ], type='http', auth="public", website=True, sitemap=True)
    def blog_apps(self, blog_name=None, tag=None, page=1, search=None, **opt):
        
        blog = request.env['blog.blog'].search([('app_project', '=', blog_name)], limit=1)
        # ~ _logger.error(f"{blog=}")
        Blog = request.env['blog.blog']
        if blog and not blog.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        domain = request.website.website_domain()
        domain += [('is_app', '=', True)]
        blogs = Blog.search(domain, order="create_date asc, id asc")
        all_blogs = Blog.search([('is_app', '=', True)], order="create_date asc, id asc")

        if not blog_name and len(blogs) == 1:
            return werkzeug.utils.redirect('/apps/%s' % blogs[0].app_project, code=302)
            # return werkzeug.utils.redirect('/apps/%s' % slug(blogs[0]), code=302)

        date_begin, date_end, state = opt.get('date_begin'), opt.get('date_end'), opt.get('state')

        if tag and request.httprequest.method == 'GET':
            # redirect get tag-1,tag-2 -> get tag-1
            tags = tag.split(',')
            if len(tags) > 1:
                url = QueryURL(
                    '' if blog else '/apps', ['blog', 'tag'],
                    blog=blog, tag=tags[0], date_begin=date_begin,
                    date_end=date_end, search=search
                )()
                return request.redirect(url, code=302)

        values = self._prepare_blog_values(
            blogs=blogs, blog=blog, date_begin=date_begin, date_end=date_end, tags=tag,
            state=state, page=page, search=search, is_app=True
        )

        # in case of a redirection need by `_prepare_blog_values` we follow it
        if isinstance(values, werkzeug.wrappers.Response):
            return values

        if blog:
            values['main_object'] = blog
            values['edit_in_backend'] = True
            values['blog_url'] = QueryURL(
                '', ['blog', 'tag'], blog=blog,
                tag=tag, date_begin=date_begin, date_end=date_end, search=search
            )
        else:
            values['blog_url'] = QueryURL(
                '/apps', ['tag'], date_begin=date_begin, date_end=date_end, search=search
            )
        return request.render("website_blog_app.blog_app_post", values)
