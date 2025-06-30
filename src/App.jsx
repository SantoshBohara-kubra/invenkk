import { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './components/Header';
import ProductList from './components/ProductList';
import Cart from './components/Cart';
import Checkout from './components/Checkout';
import { getSessionId } from './utils/sessionId';
import { buildApiUrl } from './config/api';
import { addToMockCart, getMockCart } from './data/mockData';

function App() {
  const [category, setCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showCart, setShowCart] = useState(false);
  const [showCheckout, setShowCheckout] = useState(false);
  const [cartItemCount, setCartItemCount] = useState(0);
  const [cartItems, setCartItems] = useState([]);
  const [totalPrice, setTotalPrice] = useState('0.00');
  const [sessionId] = useState(getSessionId());
  const [orderComplete, setOrderComplete] = useState(null);

  useEffect(() => {
    fetchCartCount();
  }, [sessionId]);

  const fetchCartCount = async () => {
    try {
      const response = await axios.get(buildApiUrl(`/api/cart/${sessionId}`));
      setCartItemCount(response.data.length);
    } catch (err) {
      console.warn('Backend not available, using mock cart:', err.message);
      // Fallback to mock cart
      const mockCart = getMockCart();
      setCartItemCount(mockCart.length);
    }
  };

  const handleAddToCart = async (product) => {
    try {
      await axios.post(buildApiUrl('/api/cart'), {
        product_id: product.id,
        quantity: 1,
        session_id: sessionId
      });

      fetchCartCount();

      // Show success message
      alert(`${product.name} added to cart!`);
    } catch (err) {
      console.warn('Backend not available, using mock cart:', err.message);

      // Fallback to mock cart
      addToMockCart(product.id, 1);
      fetchCartCount();

      // Show success message
      alert(`${product.name} added to cart!`);
    }
  };

  const handleSearch = (term) => {
    setSearchTerm(term);
  };

  const handleCategoryChange = (cat) => {
    setCategory(cat);
  };

  const handleCartClick = () => {
    setShowCart(true);
  };

  const handleCloseCart = () => {
    setShowCart(false);
  };

  const handleCheckout = (items, total) => {
    setCartItems(items);
    setTotalPrice(total);
    setShowCart(false);
    setShowCheckout(true);
  };

  const handleCloseCheckout = () => {
    setShowCheckout(false);
  };

  const handleOrderComplete = (order) => {
    setOrderComplete(order);
    setShowCheckout(false);
    fetchCartCount(); // Refresh cart count after order

    // Show success message
    setTimeout(() => {
      alert(`Order placed successfully! Order ID: ${order.id}`);
      setOrderComplete(null);
    }, 100);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header
        onSearch={handleSearch}
        onCategoryChange={handleCategoryChange}
        cartItemCount={cartItemCount}
        onCartClick={handleCartClick}
      />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-6">
          {category && (
            <p className="text-lg text-gray-600">
              Category: <span className="font-semibold">{category}</span>
            </p>
          )}
          {searchTerm && (
            <p className="text-lg text-gray-600">
              Search results for: <span className="font-semibold">"{searchTerm}"</span>
            </p>
          )}
        </div>

        <ProductList
          category={category}
          searchTerm={searchTerm}
          onAddToCart={handleAddToCart}
        />
      </main>

      {showCart && (
        <Cart
          sessionId={sessionId}
          onClose={handleCloseCart}
          onCheckout={handleCheckout}
        />
      )}

      {showCheckout && (
        <Checkout
          cartItems={cartItems}
          totalPrice={totalPrice}
          sessionId={sessionId}
          onClose={handleCloseCheckout}
          onOrderComplete={handleOrderComplete}
        />
      )}
    </div>
  );
}

export default App;
