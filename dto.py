class requestDTO:
    def __init__(self, method: str, url: str, headers: dict = None, body: dict = None, controller = None):
        self.method = method
        self.url = url
        self.headers = headers if headers else {}
        self.body = body if body else {}
        self.controller  = controller 
        
        
    def to_dict(self):
        return {
            "method": self.method,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "controller": self.controller if self.controller else None
        }
        