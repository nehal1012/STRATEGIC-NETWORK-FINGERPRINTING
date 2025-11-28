import requests

def get_zoomeye_data(query, query_type):
    api_key = '335682E5-0987-367AF-1C4a-21E6081d0d0'
    base_url = 'https://api.zoomeye.hk'
    
    if query_type == 'ip':
        url = f'{base_url}/host/search?query=ip:{query}&facets=app,os'
    elif query_type == 'domain':
        url = f'{base_url}/host/search?query=hostname:{query}&facets=app,os'
    elif query_type == 'port':
        url = f'{base_url}/host/search?query=port:{query}&facets=app,os'
    elif query_type == 'location':
        url = f'{base_url}/host/search?query={query}&facets=app,os'
    else:
        print(f"Invalid query type: {query_type}")
        return {"Error": "Invalid query type"}
    
    headers = {
        'Authorization': f'JWT {api_key}'
    }

    print(f"Making request to ZoomEye with URL: {url}")

    try:
        response = requests.get(url, headers=headers)
        print(f"Received response status code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {data}")
            return data
        else:
            print(f"Error response: {response.status_code} - {response.reason}")
            return {"Error": response.status_code, "Message": response.reason}
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"Error": "Request failed", "Message": str(e)}
