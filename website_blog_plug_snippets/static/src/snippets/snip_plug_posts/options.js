odoo.define('website_blog_plug_snippets.snip_plug_posts_editor', function (require) {
'use strict';

var sOptions = require('web_editor.snippets.options');
var wUtils = require('website.utils');

sOptions.registry.js_get_plug_posts = sOptions.Class.extend({

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     */
    _renderCustomXML: function (uiFragment) {
        return this._rpc({
            model: 'blog.blog',
            method: 'search_read',
            args: [wUtils.websiteDomain(this), ['name']],
        }).then(blogs => {
            const menuEl = uiFragment.querySelector('[name="blog_plug_selection"]');
            for (const blog of blogs) {
                const el = document.createElement('we-button');
                el.dataset.selectDataAttribute = blog.id;
                el.textContent = blog.name;
                menuEl.appendChild(el);
            }
        });
    },
});
});
