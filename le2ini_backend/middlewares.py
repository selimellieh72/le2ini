import logging

class LogResponseBodyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize your logging here
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        # Get the response from the view
        response = self.get_response(request)
        
        # Log the response content, be cautious with binary response
      
        self.logger.info(f"Response Body: {response.content.decode('utf-8')}")

        return response