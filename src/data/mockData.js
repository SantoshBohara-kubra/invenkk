// Mock data for when backend is not available
export const mockProducts = [
  {
    id: 1,
    name: "Wireless Bluetooth Headphones",
    description: "High-quality wireless headphones with noise cancellation",
    price: 79.99,
    image_url: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
    category: "Electronics",
    stock: 50
  },
  {
    id: 2,
    name: "Smartphone Case",
    description: "Protective case for your smartphone",
    price: 19.99,
    image_url: "https://images.unsplash.com/photo-1601593346740-925612772716?w=500",
    category: "Electronics",
    stock: 100
  },
  {
    id: 3,
    name: "Coffee Mug",
    description: "Ceramic coffee mug perfect for your morning brew",
    price: 12.99,
    image_url: "https://rusticranchfurniture.ca/cdn/shop/products/c7c9de93f674e33c5446634b9b4db32f.jpg?v=1669927284",
    category: "Home & Kitchen",
    stock: 200
  },
  {
    id: 4,
    name: "Running Shoes",
    description: "Comfortable running shoes for your daily jogs",
    price: 89.99,
    image_url: "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
    category: "Sports",
    stock: 75
  },
  {
    id: 5,
    name: "Laptop Stand",
    description: "Adjustable laptop stand for better ergonomics",
    price: 34.99,
    image_url: "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
    category: "Electronics",
    stock: 30
  },
  {
    id: 6,
    name: "Water Bottle",
    description: "Stainless steel water bottle keeps drinks cold",
    price: 24.99,
    image_url: "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=500",
    category: "Sports",
    stock: 150
  },
  {
    id: 7,
    name: "Book: Programming Guide",
    description: "Comprehensive guide to modern programming",
    price: 45.99,
    image_url: "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500",
    category: "Books",
    stock: 25
  },
  {
    id: 8,
    name: "Desk Lamp",
    description: "LED desk lamp with adjustable brightness",
    price: 39.99,
    image_url: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500",
    category: "Home & Kitchen",
    stock: 60
  }
];

export const mockCategories = ["Electronics", "Home & Kitchen", "Sports", "Books"];

// Mock cart items stored in localStorage
const CART_STORAGE_KEY = 'mini_amazon_cart';

export const getMockCart = () => {
  try {
    const cart = localStorage.getItem(CART_STORAGE_KEY);
    return cart ? JSON.parse(cart) : [];
  } catch {
    return [];
  }
};

export const setMockCart = (cartItems) => {
  try {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartItems));
  } catch (error) {
    console.error('Failed to save cart to localStorage:', error);
  }
};

export const addToMockCart = (productId, quantity = 1) => {
  const cart = getMockCart();
  const existingItem = cart.find(item => item.product_id === productId);

  if (existingItem) {
    existingItem.quantity += quantity;
  } else {
    cart.push({
      id: Date.now() + Math.random(),
      product_id: productId,
      quantity,
      product: mockProducts.find(p => p.id === productId)
    });
  }

  setMockCart(cart);
  return cart;
};

export const removeMockCartItem = (itemId) => {
  const cart = getMockCart();
  const filteredCart = cart.filter(item => item.id !== itemId);
  setMockCart(filteredCart);
  return filteredCart;
};

export const updateMockCartItem = (itemId, quantity) => {
  const cart = getMockCart();
  const item = cart.find(item => item.id === itemId);
  if (item) {
    item.quantity = quantity;
  }
  setMockCart(cart);
  return item;
};
