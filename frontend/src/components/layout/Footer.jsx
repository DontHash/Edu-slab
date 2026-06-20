/**
 * Footer Component
 * 
 * TODO:
 * 1. Add links to privacy policy, terms, etc.
 * 2. Add social media links
 * 3. Add contact information
 */

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white mt-12">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About Section */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Edu Assist </h3>
            <p className="text-gray-400">
              Adaptive learning system for personalized education.
            </p>
          </div>
          
          {/* Quick Links */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2 text-gray-400">
              <li><a href="/about" className="hover:text-white">About Us</a></li>
              <li><a href="/contact" className="hover:text-white">Contact</a></li>
              <li><a href="/help" className="hover:text-white">Help Center</a></li>
            </ul>
          </div>
          
          {/* Contact */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Contact</h3>
            <p className="text-gray-400">
              Email: support@eduadapt.com<br />
              Phone: (123) 456-7890
            </p>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2025 EduAdapt. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;