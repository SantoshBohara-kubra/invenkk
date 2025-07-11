import { useState } from 'react';
import ItemUploader from './ItemUploader';
import ItemProductList from './ItemProductList';

const DynamicHome = () => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [showUploader, setShowUploader] = useState(false);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
    setShowUploader(false);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header Row */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Product Inventory</h1>
        <div className="space-x-4">
          <button
            onClick={() => alert('Cart feature goes here')}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
          >
            Cart
          </button>
          <button
            onClick={() => setShowUploader(true)}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
          >
            Add New Product
          </button>
        </div>
      </div>

      {/* Product Grid */}
      <ItemProductList
        key={refreshKey}
        onAddToCart={(product) => console.log('Add to cart:', product)}
      />

      {/* Modal Popup */}
      {showUploader && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white rounded-lg shadow-lg w-full max-w-2xl p-6 relative">
            <button
              className="absolute top-3 right-3 text-gray-600 hover:text-black text-xl"
              onClick={() => setShowUploader(false)}
            >
              &times;
            </button>
            <ItemUploader onProductUpload={handleRefresh} />
          </div>
        </div>
      )}
    </div>
  );
};

export default DynamicHome;
