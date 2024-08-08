import mimetypes
import tempfile
from functools import partial, partialmethod
import json
import random
import string
import requests
import moviepy.editor
from uuid import uuid4
from ensta.Guest import Guest
from pathlib import Path
from json import JSONDecodeError
from ensta.containers.Liker import Liker
from ensta.containers.Likers import Likers
from ensta.containers.Post import Post
from collections.abc import Generator
from ensta.containers.ProfileHost import ProfileHost
from ensta.containers.PrivateInfo import PrivateInfo
from ensta.containers.PostDetail import PostDetail
from ensta.containers import (FollowedStatus, UnfollowedStatus, FollowPerson, PhotoUpload, ReelUpload)
from ensta.lib import (
    SessionError,
    NetworkError,
    IdentifierError,
    DevelopmentError,
    APIError,
    ConversionError
)
from PIL import Image
from ensta.lib.Searcher import create_search_obj, search_comments
from ensta import Web, WebSession
from urllib.parse import urlparse, parse_qs
from ensta.Utils import time_id, fb_uploader
from pyquery import PyQuery

IMAGE_RUPLOAD_PARAMS = {
    "retry_context": "{\"num_step_auto_retry\": 0, \"num_reupload\": 0, \"num_step_manual_retry\": 0}",
    "media_type": "1",
    "image_compression": json.dumps({"lib_name": "moz", "lib_version": "3.1.m", "quality": 80})
}

REEL_RUPLOAD_PARAMS = {
    "retry_context": "{\"num_step_auto_retry\": 0, \"num_reupload\": 0, \"num_step_manual_retry\": 0}",
    "is_clips_video": "1",
    "media_type": "2",
}

CAROUSEL_VIDEO_RUPLOAD_PARAMS = {
    "retry_context": "{\"num_step_auto_retry\": 0, \"num_reupload\": 0, \"num_step_manual_retry\": 0}",
    "is_unified_video": "0",
    "is_clips_video": "0",
    "is_sidecar": "1",
    "media_type": "2",
}


class CustomWeb(Web):
    def pub_photo(
            self,
            upload_id: str,
            caption: str = "",
            alt_text: str = "",
            archive_only: bool = False,
            disable_comments: bool = False,
            like_and_view_counts_disabled: bool = False
    ) -> PhotoUpload:
        """
        Creates a single photo post on your account.
        :param upload_id: Upload ID of file already uploaded using get_upload_id() method
        :param caption: Optional caption text for current post
        :param alt_text: Optional custom accessibility caption for this photo
        :param archive_only: Boolean (Should this post be directly archived)
        :param disable_comments: Boolean (Should comments on this post be disabled)
        :param like_and_view_counts_disabled: Boolean (Shouldn't people be able to see how many users liked & viewed this post)
        :return: PostUpload
        """

        request_headers: dict = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            "dpr": "1.30208",
            "sec-ch-prefers-color-scheme": "dark",
            "sec-ch-ua": self.user_agent,
            "sec-ch-ua-full-version-list": self.user_agent,
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-model": "\"\"",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-ch-ua-platform-version": "\"15.0.0\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "viewport-width": "1475",
            "x-asbd-id": "129477",
            "x-csrftoken": self.csrf_token,
            "x-ig-app-id": self.insta_app_id,
            "x-ig-www-claim": self.x_ig_www_claim,
            "x-instagram-ajax": "1009848613",
            "x-requested-with": "XMLHttpRequest",
            "Referer": "https://www.instagram.com/",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

        body_json = {
            "archive_only": archive_only,
            "caption": caption,
            "clips_share_preview_to_feed": "1",
            "disable_comments": "1" if disable_comments else "0",
            "disable_oa_reuse": False,
            "igtv_share_preview_to_feed": "1",
            "is_meta_only_post": "0",
            "is_unified_video": "1",
            "like_and_view_counts_disabled": "1" if like_and_view_counts_disabled else "0",
            "source_type": "library",
            "upload_id": upload_id,
            "video_subtitles_enabled": "0"
        }

        if alt_text != "": body_json["custom_accessibility_caption"] = alt_text

        http_response = self.request_session.post(
            "https://www.instagram.com/api/v1/media/configure/",
            headers=request_headers,
            data=body_json
        )

        try:
            response_json: dict = http_response.json()
            return PhotoUpload.from_response_data(response_json)

        except JSONDecodeError:
            raise NetworkError("Response not a valid json.")

    def _upload_image(self, media: str, upload_id: str | None = None, **kwargs) -> str:
        """
        https://i.instagram.com/rupload_igphoto/
        """
        rupload_params = dict(kwargs)
        media_path: Path = Path(media)
        mimetype, _ = mimetypes.guess_type(media_path)
        upload_id = upload_id or time_id()
        waterfall_id = str(uuid4())
        upload_name = fb_uploader(upload_id)
        rupload_params.update(**{
            "upload_id": upload_id,
            "xsharing_user_ids": json.dumps([self.user_id]),
        })

        with open(media_path, "rb") as file:
            image_data = file.read()
            image_length = str(len(image_data))

        request_headers = {
            "accept-encoding": "gzip",
            "x-instagram-rupload-params": json.dumps(rupload_params),
            "x_fb_photo_waterfall_id": waterfall_id,
            "x-entity-type": mimetype,
            "offset": "0",
            "x-entity-name": upload_name,
            "x-entity-length": image_length,
            "content-type": mimetype,
            "content-length": image_length
        }

        http_response = self.request_session.post(
            f"https://i.instagram.com/rupload_igphoto/{upload_name}",
            data=image_data,
            headers=request_headers
        )

        try:
            response_json: dict = http_response.json()

            if response_json.get("status", "") != "ok":
                raise NetworkError("Response json key 'status' not ok.")
            if response_json.get("upload_id", "") == "":
                raise NetworkError(
                    "Key 'upload_id' in response json doesn't exist or is invalid."
                )

            return str(response_json.get("upload_id"))

        except JSONDecodeError:
            raise NetworkError("Response not a valid json.")

    upload_image = partialmethod(_upload_image, **IMAGE_RUPLOAD_PARAMS)
