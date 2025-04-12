from model import CurrencyModel

class Controller:

    def get_currencies(self):
        currencies = self.model.get_currencies()  # Получаем список словарей
        self.send_json_response(200, currencies)  # Используем send_json_response
        
    def get_currency_by_code(self, code):
        pass
            
    def get_exchange_rates(self):
        pass
    
    def handle_html_page(self, obj):
        print('Hello')
        obj.send_response(200)
        obj.send_header('Content-Type', 'text/html')
        obj.end_headers()
        with open('index.html', 'r', encoding='utf-8') as file:
            html_content = file.read()
        obj.wfile.write(html_content.encode())
        
