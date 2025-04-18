import logging
from django.http import FileResponse

class LogResponseBodyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        response = self.get_response(request)

        if hasattr(response, 'content') and not isinstance(response, FileResponse):
            try:
                body = response.content.decode('utf-8')
                self.logger.info(f"Response Body: {body}")
            except UnicodeDecodeError:
                self.logger.warning("Response content could not be decoded as UTF-8.")
        else:
            self.logger.debug(f"Skipped logging response body for path: {request.path} (streamed or binary content)")

        return response