from odoo import models, fields, api, _
import requests
import tempfile
import os
import logging
from ensta import Web
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.exceptions import ValidationError, UserError

# from odoo.addons.blog_instagram.ensta.CustomWeb import CustomWeb


INSTAGRAM_URL = "https://www.instagram.com/p"


def _download_image_to_temp_file(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

        # Check content type for image
        if 'image' not in response.headers.get('Content-Type', ''):
            raise Exception("URL does not contain an image")

        # Extract the file extension from the URL
        _, file_extension = os.path.splitext(url)

        # Verify if the file extension is acceptable
        if file_extension.lower() not in ['.jpg', '.jpeg', '.png']:
            raise Exception("Unsupported image format")

        # Create a temporary file with the correct extension
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
        temp_file.write(response.content)
        temp_file.close()

        # Optional: Validate the image by opening it with PIL or another image library

        return temp_file.name
    except Exception as e:
        raise Exception(f"Failed to retrieve image from {url}: {str(e)}")


class BlogPost(models.Model):
    _inherit = 'blog.post'

    ig_post_id = fields.Char(string="IG Post ID")

    def action_open_form(self):
        self.ensure_one()
        return {
            'name': self.name,
            'view_mode': 'form',
            'res_model': 'blog.post',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

    def _authenticate_params(self):
        user_name = self.env['ir.config_parameter'].sudo().get_param('ig.username').strip()
        password = self.env['ir.config_parameter'].sudo().get_param('ig.password').strip()
        if not user_name or not password:
            raise UserError(_("Instagram Username or Password is not set. Check System Parameters"))
        return user_name, password

    def _establish_ensta_con(self):
        user_name, password = self._authenticate_params()
        ig_connection = Web(user_name, password)
        return ig_connection

    def action_post_on_instagram(self):
        ig = self._establish_ensta_con()

        blog_image = json_scriptsafe.loads(self.cover_properties).get('background-image', 'none')[4:-1].strip("'")
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        img_path = _download_image_to_temp_file(f"{base_url}{blog_image}")

        try:
            photo_upload_id = ig.upload_image(img_path)
            ig_post_id = ig.pub_photo(
                upload_id=photo_upload_id,
                caption=self.subtitle
            )

            self.ig_post_id = ig_post_id.code
            chatter_msg = f"Post URL: {INSTAGRAM_URL}/{self.ig_post_id} <br/> Post ID: {ig_post_id.pk}"
            self.message_post(body=chatter_msg)
        except Exception as e:
            raise ValidationError(_(e))

    def action_view_post_on_instagram(self):
        url = f"{INSTAGRAM_URL}/{self.ig_post_id}"
        return {
            "name": "IG Post",
            "type": "ir.actions.act_url",
            "url": url,
        }

    def fetch_posts(self):
        ig = self._establish_ensta_con()
        posts = ig.posts("vertel_ab")

        for post in posts:
            logging.info(f"Post URL: {post.share_url}")
            logging.info(f"Post ID: {post.post_id}")
