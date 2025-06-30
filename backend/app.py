from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configure CORS to allow requests from frontend
CORS(app, origins=['http://localhost:5173'])

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///mini_amazon.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
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
    session_id = db.Column(db.String(100), nullable=False)  # Simple session tracking
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
    price = db.Column(db.Float, nullable=False)  # Price at time of order

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

# API Routes
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

    # Check if item already exists in cart
    existing_item = CartItem.query.filter_by(
        product_id=product_id,
        session_id=session_id
    ).first()

    if existing_item:
        existing_item.quantity += quantity
    else:
        cart_item = CartItem(
            product_id=product_id,
            quantity=quantity,
            session_id=session_id
        )
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

    # Get cart items
    cart_items = CartItem.query.filter_by(session_id=session_id).all()

    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    # Calculate total
    total_amount = sum(item.product.price * item.quantity for item in cart_items)

    # Create order
    order = Order(
        session_id=session_id,
        total_amount=total_amount,
        shipping_address=shipping_address
    )
    db.session.add(order)
    db.session.flush()  # Get order ID

    # Create order items
    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.session.add(order_item)

    # Clear cart
    CartItem.query.filter_by(session_id=session_id).delete()

    db.session.commit()
    return jsonify(order.to_dict())

@app.route('/api/orders/<session_id>', methods=['GET'])
def get_orders(session_id):
    orders = Order.query.filter_by(session_id=session_id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Add sample data if no products exist
        if Product.query.count() == 0:
            sample_products = [
                Product(name="Wireless Bluetooth Headphones", description="High-quality wireless headphones with noise cancellation", price=79.99, image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500", category="Electronics", stock=50),
                Product(name="Smartphone Case", description="Protective case for your smartphone", price=19.99, image_url="https://images.unsplash.com/photo-1601593346740-925612772716?w=500", category="Electronics", stock=100),
                Product(name="Coffee Mug", description="Ceramic coffee mug perfect for your morning brew", price=12.99, image_url="https://images.unsplash.com/photo-1514228742587-6b1558fcf93a?w=500", category="Home & Kitchen", stock=200),
                Product(name="Running Shoes", description="Comfortable running shoes for your daily jogs", price=89.99, image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500", category="Sports", stock=75),
                Product(name="Laptop Stand", description="Adjustable laptop stand for better ergonomics", price=34.99, image_url="https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500", category="Electronics", stock=30),
                Product(name="Water Bottle", description="Stainless steel water bottle keeps drinks cold", price=24.99, image_url="https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500", category="Sports", stock=150),
                Product(name="Book: Programming Guide", description="Comprehensive guide to modern programming", price=45.99, image_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500", category="Books", stock=25),
                Product(name="Desk Lamp", description="LED desk lamp with adjustable brightness", price=39.99, image_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500", category="Home & Kitchen", stock=60)
            ]

            for product in sample_products:
                db.session.add(product)
            db.session.commit()

    app.run(debug=True, host='0.0.0.0', port=5000)
