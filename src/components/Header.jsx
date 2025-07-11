import { useState, useEffect } from 'react';
import axios from 'axios';
import { buildApiUrl } from '../config/api';

const Header = ({
  onSearch,
  onCategoryChange,
  cartItemCount,
  onCartClick,
  onAddProductClick
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [categories, setCategories] = useState(['All Categories']);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(buildApiUrl('/api/categories'));
      setCategories(['All Categories', ...response.data]);
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    onSearch(searchTerm);
  };

  return (
    <header className="bg-gray-900 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        {/* Top row with logo, buttons */}
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-3xl font-bold text-yellow-400">Mini Amazon</h1>
          <div className="flex items-center gap-4">
            <button
              onClick={onAddProductClick}
              className="bg-green-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-400 transition-colors"
            >
              Add New Product
            </button>
            <button
              onClick={onCartClick}
              className="relative bg-yellow-500 text-gray-900 px-4 py-2 rounded-lg font-medium hover:bg-yellow-400 transition-colors"
            >
              Cart
              {cartItemCount > 0 && (
                <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center">
                  {cartItemCount}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Search + Categories */}
        <div className="flex flex-col md:flex-row gap-4">
          <form onSubmit={handleSearchSubmit} className="flex-1 flex">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search products..."
              className="flex-1 px-4 py-2 rounded-l-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-yellow-400"
            />
            <button
              type="submit"
              className="bg-yellow-500 text-gray-900 px-6 py-2 rounded-r-lg font-medium hover:bg-yellow-400 transition-colors"
            >
              Search
            </button>
          </form>

          <select
            onChange={(e) =>
              onCategoryChange(e.target.value === 'All Categories' ? '' : e.target.value)
            }
            className="px-4 py-2 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-yellow-400"
          >
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>
    </header>
  );
};

export default Header;
