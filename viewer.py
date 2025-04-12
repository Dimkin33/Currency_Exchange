from router import Router
from urllib.parse import urlparse, parse_qs
#from app_server import RequestHandler

class Viewer:
    def to_server(self, obj) -> tuple:
        parsed_path = urlparse(obj.path)
        query_params = parse_qs(parsed_path.query)
        print(f'get query_params 444=  {query_params},  path = {parsed_path.path}')
        
        router = Router(obj).resolve()
        print('router = ', type(router))
        router(obj)
        return router
    