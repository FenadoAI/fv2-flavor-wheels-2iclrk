import { useEffect, useState } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Phone, Mail, Instagram, Facebook, MapPin, Clock, Star, ShoppingCart } from "lucide-react";

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const API = `${API_BASE}/api`;

// Header Component
const Header = ({ foodTruckInfo }) => (
  <header className="bg-gradient-to-r from-orange-500 to-red-600 text-white shadow-lg">
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row items-center justify-between">
        <div className="text-center md:text-left mb-4 md:mb-0">
          <h1 className="text-4xl md:text-5xl font-bold mb-2">
            {foodTruckInfo?.name || "Loading..."}
          </h1>
          <p className="text-xl opacity-90">
            {foodTruckInfo?.description || ""}
          </p>
        </div>
        <div className="flex flex-col space-y-2 text-center md:text-right">
          {foodTruckInfo?.phone && (
            <div className="flex items-center justify-center md:justify-end space-x-2">
              <Phone size={20} />
              <span className="text-lg">{foodTruckInfo.phone}</span>
            </div>
          )}
          {foodTruckInfo?.email && (
            <div className="flex items-center justify-center md:justify-end space-x-2">
              <Mail size={20} />
              <span>{foodTruckInfo.email}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  </header>
);

// Hero Section Component
const HeroSection = () => (
  <section className="relative h-96 bg-cover bg-center flex items-center justify-center"
    style={{
      backgroundImage: `linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), url('https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=1200&q=80')`
    }}>
    <div className="text-center text-white">
      <h2 className="text-5xl font-bold mb-4">Fresh Food, Bold Flavors</h2>
      <p className="text-xl mb-6">Experience the best street food in the city</p>
      <Button size="lg" className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 text-lg">
        View Our Menu
      </Button>
    </div>
  </section>
);

// Menu Section Component
const MenuSection = ({ menuItems }) => {
  const categories = [...new Set(menuItems.map(item => item.category))];

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center mb-12 text-gray-800">Our Menu</h2>
        {categories.map(category => (
          <div key={category} className="mb-12">
            <h3 className="text-2xl font-semibold mb-6 text-orange-600">{category}</h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {menuItems
                .filter(item => item.category === category)
                .map(item => (
                  <Card key={item.id} className="hover:shadow-lg transition-shadow">
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <CardTitle className="text-xl">{item.name}</CardTitle>
                        <Badge variant={item.available ? "default" : "secondary"}>
                          {item.available ? "Available" : "Sold Out"}
                        </Badge>
                      </div>
                      <CardDescription className="text-base">
                        {item.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex justify-between items-center">
                        <span className="text-2xl font-bold text-green-600">
                          ${item.price.toFixed(2)}
                        </span>
                        <Button
                          disabled={!item.available}
                          className="bg-orange-500 hover:bg-orange-600"
                        >
                          <ShoppingCart size={16} className="mr-2" />
                          Add to Cart
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

// Locations Section Component
const LocationsSection = ({ locations }) => (
  <section className="py-16">
    <div className="container mx-auto px-4">
      <h2 className="text-4xl font-bold text-center mb-12 text-gray-800">Find Us</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {locations.map(location => (
          <Card key={location.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <MapPin size={20} className="text-orange-500" />
                <span>{location.name}</span>
              </CardTitle>
              <CardDescription>{location.address}</CardDescription>
            </CardHeader>
            <CardContent>
              {location.schedule && (
                <div className="flex items-center space-x-2 mb-4">
                  <Clock size={16} className="text-gray-500" />
                  <span className="text-sm text-gray-600">{location.schedule}</span>
                </div>
              )}
              <Badge variant={location.active ? "default" : "secondary"}>
                {location.active ? "Active" : "Inactive"}
              </Badge>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  </section>
);

// Social Media Section
const SocialMediaSection = ({ socialMedia }) => (
  <section className="py-12 bg-gray-800 text-white">
    <div className="container mx-auto px-4 text-center">
      <h2 className="text-3xl font-bold mb-8">Follow Us</h2>
      <div className="flex justify-center space-x-6">
        {socialMedia?.instagram && (
          <a href={`https://instagram.com/${socialMedia.instagram.replace('@', '')}`}
             target="_blank" rel="noopener noreferrer"
             className="flex items-center space-x-2 hover:text-orange-400 transition-colors">
            <Instagram size={24} />
            <span>{socialMedia.instagram}</span>
          </a>
        )}
        {socialMedia?.facebook && (
          <a href={`https://facebook.com/${socialMedia.facebook}`}
             target="_blank" rel="noopener noreferrer"
             className="flex items-center space-x-2 hover:text-orange-400 transition-colors">
            <Facebook size={24} />
            <span>{socialMedia.facebook}</span>
          </a>
        )}
      </div>
    </div>
  </section>
);

// Footer Component
const Footer = () => (
  <footer className="bg-gray-900 text-white py-8">
    <div className="container mx-auto px-4 text-center">
      <p>&copy; 2024 Food Truck. All rights reserved.</p>
      <p className="mt-2 text-gray-400">Made with ❤️ for food lovers</p>
    </div>
  </footer>
);

// Main Home Component
const Home = () => {
  const [foodTruckInfo, setFoodTruckInfo] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [infoResponse, menuResponse, locationsResponse] = await Promise.all([
        axios.get(`${API}/foodtruck`),
        axios.get(`${API}/menu`),
        axios.get(`${API}/locations`)
      ]);

      setFoodTruckInfo(infoResponse.data);
      setMenuItems(menuResponse.data);
      setLocations(locationsResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header foodTruckInfo={foodTruckInfo} />
      <HeroSection />
      <MenuSection menuItems={menuItems} />
      <LocationsSection locations={locations} />
      <SocialMediaSection socialMedia={foodTruckInfo?.social_media} />
      <Footer />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
