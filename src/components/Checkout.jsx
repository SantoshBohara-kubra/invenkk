import { useState } from 'react';
import axios from 'axios';
import { buildApiUrl } from '../config/api';
import { setMockCart } from '../data/mockData';

const Checkout = ({ cartItems, totalPrice, sessionId, onClose, onOrderComplete }) => {
  const [shippingAddress, setShippingAddress] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!shippingAddress.trim()) {
      setError('Please enter a shipping address');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await axios.post(buildApiUrl('/api/orders'), {
        session_id: sessionId,
        shipping_address: shippingAddress
      });

      onOrderComplete(response.data);
    } catch (err) {
      console.warn('Backend not available, using mock order:', err.message);

      // Fallback to mock order
      const mockOrder = {
        id: Date.now(),
        session_id: sessionId,
        total_amount: parseFloat(totalPrice),
        status: 'pending',
        shipping_address: shippingAddress,
        created_at: new Date().toISOString()
      };

      // Clear mock cart
      setMockCart([]);

      onOrderComplete(mockOrder);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold">Checkout</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <div className="mb-6">
            <h3 className="font-semibold mb-2">Order Summary</h3>
            <div className="space-y-2">
              {cartItems.map((item) => (
                <div key={item.id} className="flex justify-between text-sm">
                  <span>{item.product.name} x {item.quantity}</span>
                  <span>${(item.product.price * item.quantity).toFixed(2)}</span>
                </div>
              ))}
              <div className="border-t pt-2 font-bold">
                Total: ${totalPrice}
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
                Shipping Address *
              </label>
              <textarea
                id="address"
                value={shippingAddress}
                onChange={(e) => setShippingAddress(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
                placeholder="Enter your full shipping address..."
                required
              />
            </div>

            <div className="bg-gray-50 p-4 rounded-lg mb-4">
              <p className="text-sm text-gray-600">
                <strong>Note:</strong> This is a demo checkout. No actual payment will be processed.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full py-3 rounded-lg font-semibold transition-colors ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700'
              } text-white`}
            >
              {loading ? 'Placing Order...' : 'Place Order'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
