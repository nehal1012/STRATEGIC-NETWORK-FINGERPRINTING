from my_flask_app import Flask, render_template, request
import re
import shodan
import requests
import base64

app = Flask(__name__)

# Shodan API Key (replace with your actual API key)
SHODAN_API_KEY = 'XxbMZReR9r3DU8BDwEXIef04lPiGLlMq'
shodan_api = shodan.Shodan(SHODAN_API_KEY)

# ZoomEye API Key (replace with your actual API key)
ZOOMYE_API_KEY = '335682E5-0987-367AF-1C4a-21E6081d0d0'

# Hunter API Key (replace with your actual API key)
HUNTER_API_KEY = '4670e684ee54dfd155b115af260a27307899bcba006f68e3fda7d34a12e3d361'

# Define the URL and IP pattern for validation
url_pattern = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9?\.]+)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# Base64 URL encode the query
def base64_url_encode(query):
    encoded_bytes = base64.urlsafe_b64encode(query.encode('utf-8'))
    encoded_str = str(encoded_bytes, 'utf-8').rstrip('=')
    return encoded_str

# Define the function to query Hunter API for a given query
def get_hunter_data(query):
    encoded_query = base64_url_encode(query)
    start_time = '2024-01-01'
    end_time = '2024-06-01'
    url = f'https://api.hunter.how/search?api-key={HUNTER_API_KEY}&query={encoded_query}&start_time={start_time}&end_time={end_time}'
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"Error": response.status_code, "Message": response.reason}
    except requests.exceptions.RequestException as e:
        return {"Error": "Request failed", "Message": str(e)}

# Define the route for handling requests to the root URL
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        if re.match(url_pattern, query):
            # It's a valid URL
            url_info = get_url_info(query)
            return render_template('results.html', url_info=url_info, type='url')
        elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
            # Assume it's a domain
            shodan_info = get_shodan_domain_info(query)
            zoomeye_info = get_zoomeye_data(query, 'domain')
            hunter_info = get_hunter_data(query)
            return render_template('results.html', shodan_info=shodan_info, zoomeye_info=zoomeye_info, hunter_info=hunter_info, type='domain')
        else:
            # Assume it's an IP address
            shodan_info = get_shodan_info(query)
            zoomeye_info = get_zoomeye_data(query, 'ip')
            hunter_info = get_hunter_data(query)
            return render_template('results.html', shodan_info=shodan_info, zoomeye_info=zoomeye_info, hunter_info=hunter_info, type='ip')
    return render_template('index.html')

# Define functions to fetch data from Shodan and ZoomEye
def get_shodan_info(ip):
    try:
        host = shodan_api.host(ip)
        return host
    except shodan.APIError as e:
        return {'error': str(e)}

def get_shodan_domain_info(domain):
    url = f'https://api.shodan.io/dns/domain/{domain}?key={SHODAN_API_KEY}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.status_code, "message": response.reason}
    except requests.exceptions.RequestException as e:
        return {"error": "Request failed", "message": str(e)}

def get_zoomeye_data(query, query_type):
    base_url = 'https://api.zoomeye.hk'
    
    if query_type == 'ip':
        url = f'{base_url}/host/search?query=ip:{query}&facets=app,os&API={ZOOMYE_API_KEY}'
    elif query_type == 'domain':
        url = f'{base_url}/host/search?query=hostname:{query}&facets=app,os&API={ZOOMYE_API_KEY}'
    elif query_type == 'port':
        url = f'{base_url}/host/search?query=port:{query}&facets=app,os&API={ZOOMYE_API_KEY}'
    elif query_type == 'location':
        url = f'{base_url}/host/search?query={query}&facets=app,os&API={ZOOMYE_API_KEY}'
    else:
        return {"Error": "Invalid query type"}
    
    headers = {
        'API-KEY': ZOOMYE_API_KEY
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"Error": response.status_code, "Message": response.reason}
    except requests.exceptions.RequestException as e:
        return {"Error": "Request failed", "Message": str(e)}

def get_url_info(url):
    # Dummy implementation for URL info retrieval
    return {"url": url, "info": "This is a dummy implementation."}

if __name__ == '__main__':
    app.run(debug=True)
    