from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

catalog_server_url = 'http://127.0.0.1:5100'

@app.route('/')
def home():
    return jsonify(message="Order Server is Running")

# Purchase book endpoint
@app.route('/purchase/<int:book_id>', methods=['PUT'])
def purchase_book(book_id):
    # Retrieve book information from the catalog server
    catalog_response = requests.put(f"{catalog_server_url}/update/{book_id}")
    
    # Check if the book information is retrieved successfully
    if catalog_response.status_code == 200:
        # Process the purchase logic here
        # For now, just return the catalog response
        return catalog_response.json()
    else:
        return jsonify(catalog_response.json()),catalog_response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=5200)
