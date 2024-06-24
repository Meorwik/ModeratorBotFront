from forms.enums import AllowedContentTypes
from aiogram.types import Message
from .base import BaseValidator


class MediaValidator(BaseValidator):

    __name__: str = "MediaValidator"

    def _validate(self, value: Message) -> (bool, AllowedContentTypes):
        if value.content_type == AllowedContentTypes.text.value:
            return True

        elif value.content_type == AllowedContentTypes.document.value:
            return True

        elif value.content_type == AllowedContentTypes.video.value:
            return True

        elif value.content_type == AllowedContentTypes.photo.value:
            return True

        else:
            return False

    def has_media(self, value: Message) -> bool:
        return not value.content_type == AllowedContentTypes.text
