from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173'])

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mini_amazon.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'category': self.category,
            'stock': self.stock,
            'created_at': self.created_at.isoformat()
        }

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    session_id = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', backref='cart_items')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'session_id': self.session_id,
            'product': self.product.to_dict() if self.product else None,
            'created_at': self.created_at.isoformat()
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    shipping_address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'total_amount': self.total_amount,
            'status': self.status,
            'shipping_address': self.shipping_address,
            'created_at': self.created_at.isoformat()
        }

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref='items')
    product = db.relationship('Product')

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price,
            'product': self.product.to_dict() if self.product else None
        }

# API Endpoints
@app.route('/api/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    category = request.args.get('category', type=str)
    search = request.args.get('search', type=str)

    query = Product.query
    if category:
        query = query.filter(Product.category == category)
    if search:
        query = query.filter(Product.name.contains(search))

    products = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'products': [product.to_dict() for product in products.items],
        'total': products.total,
        'pages': products.pages,
        'current_page': products.page
    })

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict())

@app.route('/api/categories', methods=['GET'])
def get_categories():
    # Returns a unique list of non-null categories
    categories = db.session.query(Product.category).distinct().all()
    return jsonify([cat[0] for cat in categories if cat[0]])

@app.route('/api/cart/<session_id>', methods=['GET'])
def get_cart(session_id):
    cart_items = CartItem.query.filter_by(session_id=session_id).all()
    return jsonify([item.to_dict() for item in cart_items])

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    session_id = data.get('session_id')

    if not all([product_id, session_id]):
        return jsonify({'error': 'Missing required fields'}), 400

    existing_item = CartItem.query.filter_by(product_id=product_id, session_id=session_id).first()

    if existing_item:
        existing_item.quantity += quantity
    else:
        cart_item = CartItem(product_id=product_id, quantity=quantity, session_id=session_id)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({'message': 'Item added to cart successfully'})

@app.route('/api/cart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    data = request.get_json()
    quantity = data.get('quantity')
    cart_item = CartItem.query.get_or_404(item_id)
    cart_item.quantity = quantity
    db.session.commit()
    return jsonify(cart_item.to_dict())

@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({'message': 'Item removed from cart'})

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    session_id = data.get('session_id')
    shipping_address = data.get('shipping_address', '')

    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400

    cart_items = CartItem.query.filter_by(session_id=session_id).all()
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    order = Order(session_id=session_id, total_amount=total_amount, shipping_address=shipping_address)
    db.session.add(order)
    db.session.flush()

    for cart_item in cart_items:
        if cart_item.product.stock >= cart_item.quantity:
            cart_item.product.stock -= cart_item.quantity
        else:
            return jsonify({'error': f'Not enough stock for {cart_item.product.name}'}), 400

        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.session.add(order_item)

    CartItem.query.filter_by(session_id=session_id).delete()

    db.session.commit()
    return jsonify(order.to_dict())

@app.route('/api/orders/<session_id>', methods=['GET'])
def get_orders(session_id):
    orders = Order.query.filter_by(session_id=session_id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/upload-item', methods=['POST'])
def upload_item():
    data = request.get_json()
    required_fields = ['name', 'price', 'stock']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    existing_product = Product.query.filter_by(name=data['name']).first()
    if existing_product:
        existing_product.stock += int(data['stock'])
    else:
        new_product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=float(data['price']),
            image_url=data.get('image_url', ''),
            category=data.get('category', ''),
            stock=int(data['stock'])
        )
        db.session.add(new_product)

    db.session.commit()
    return jsonify({'message': 'Inventory updated successfully'}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
