from flask import Flask, jsonify, request  # Added jsonify and request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.db'  # Updated the database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    topic = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Book {self.title}>'

    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'quantity': self.quantity,
            'price': self.price,
            'topic': self.topic
        }

@app.route('/')
def home():
    return jsonify(message="Catalog Server is Running")

# Add book endpoint
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()  # Ensure request is used here for getting JSON data
    new_book = Book(
        title=data['title'],
        author=data['author'],
        quantity=data['quantity'],
        price=data['price'],
        topic=data.get('topic', '')  # Use .get to avoid KeyError if 'topic' is not provided
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully', 'book': str(new_book)}), 201

# Get all books endpoint
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    output = [{
        'id': book.id, 
        'title': book.title, 
        'author': book.author, 
        'quantity': book.quantity, 
        'price': book.price,
        'topic': book.topic  # Include topic in the response
    } for book in books]
    return jsonify({'books': output})

# Get single book by ID endpoint
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get_or_404(id)
    return jsonify({
        'id': book.id, 
        'title': book.title, 
        'author': book.author, 
        'quantity': book.quantity, 
        'price': book.price,
        'topic': book.topic  # Include topic in the response
    })

# DELETE single book by ID endpoint
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully'}), 200

# Update single book by ID endpoint

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get_or_404(id)
    data = request.get_json()
    book.price = data.get('price', book.price)  # Update price if provided
    book.quantity = data.get('quantity', book.quantity)  # Update quantity instead of stock
    db.session.commit()
    return jsonify(book.serialize())  # Ensure you have a serialize method to convert the book object to a dictionary
#search(topic)
@app.route('/search/<string:topic>', methods=['GET'])
def search_by_topic(topic):
    books = Book.query.filter_by(topic=topic).all()
    if books:
        result = [{'id': book.id, 'title': book.title} for book in books]
        return jsonify({'message': 'Books found', 'books': result}), 200
    else:
        return jsonify({'message': 'No books found for the given topic'}), 404

#purchase(item_number)
@app.route('/purchase/<int:id>', methods=['PUT'])
def purchase_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'message': 'Book not found'}), 404
    if book.quantity <= 0:
        return jsonify({'message': 'Book out of stock'}), 400

    book.quantity -= 1  # Decrement the stock
    db.session.commit()  # Save the changes
    return jsonify({'message': 'Purchase successful'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5100)
