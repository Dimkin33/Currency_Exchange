from dto import requestDTO
from controller import Controller
#from app_server import RequestHandler
class Router:
    
    
    def __init__(self, obj):
        self.obj = obj
        self.route_path = {'/'              : Controller().handle_html_page,
                            '/currencies'   : Controller().get_currencies
                            
                        }
    
    def resolve(self):
        self.obj.controller = self.route_path.get(self.obj.url, None)
        return None
        
    
