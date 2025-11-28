import requests

# Define the function to query Shodan API for a given IP address
def get_shodan_data(ip_address):
    # Replace with your actual Shodan API key
    api_key = '0dSWtaOzZmw9myp8nvD0lWtvlBlLWvfm'
    
    # Define the URL of the Shodan API endpoint with the IP address
    url = f'https://api.shodan.io/shodan/host/{ip_address}?key={api_key}'
    
    try:
        # Make a GET request to the Shodan API
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

# Main function to prompt user for an IP address and display information
def main():
    # Prompt the user to input an IP address
    ip_address = input("Enter an IP address: ")
    
    # Get the Shodan data for the provided IP address
    shodan_data = get_shodan_data(ip_address)
    
    # Display the results
    if "Error" in shodan_data:
        print(f"Error: {shodan_data['Message']}")
    else:
        print(f"IP: {shodan_data.get('ip_str', 'N/A')}")
        print(f"Organization: {shodan_data.get('org', 'N/A')}")
        print(f"ISP: {shodan_data.get('isp', 'N/A')}")

# Run the main function
if __name__ == "__main__":
    main()
