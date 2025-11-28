from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Handle POST request
        return 'POST request received'
    return 'GET request received'

if __name__ == '__main__':
    app.run(debug=True)
