import requests
import base64

# Function to base64 URL encode the query
def base64_url_encode(query):
    encoded_bytes = base64.urlsafe_b64encode(query.encode('utf-8'))
    encoded_str = str(encoded_bytes, 'utf-8').rstrip('=')
    return encoded_str

# Define the function to query Hunter API for a given query
def get_hunter_data(query):
    # Replace with your actual Hunter API key
    api_key = '63401de3f3ad7d411f86d89a195c135536734e79126d693d7efff34133551b78'
    
    # Base64 URL encode the query
    encoded_query = base64_url_encode(query)
    
    # Define the URL of the Hunter API endpoint with the encoded query
    start_time = '2024-01-01'
    end_time = '2024-06-01'
    url = url = f'https://api.hunter.io/v2/domain-search?domain={encoded_query}&api_key={api_key}'
    
    try:
        # Make a GET request to the Hunter API
        response = requests.get(url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract data from the response (assuming it's JSON)
            data = response.json()
            
            # Return the data
            return data
        else:
            # If the request was not successful, return the error status code
            return {"Error": response.status_code, "Message": response.reason}
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        return {"Error": "Request failed", "Message": str(e)}

# Main function to prompt user for a query and display information
def main():
    # Prompt the user to input a query
    query = input("Enter a query (e.g., google.com or 192.168.1.1): ")
    
    # Get the Hunter data for the provided query
    hunter_data = get_hunter_data(query)
    
    # Display the results
    print(hunter_data)

# Run the main function
if __name__ == "__main__":
    main()