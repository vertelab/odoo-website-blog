/** @odoo-module **/

import options from "@web_editor/js/editor/snippets.options";
import weUtils from "@web_editor/js/common/utils";


options.registry.js_get_plug_posts = options.Class.extend({

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
