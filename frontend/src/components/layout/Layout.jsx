/**
 * Main Layout Component
 * 
 * Wraps all pages with Header, Sidebar (optional), and Footer
 * 
 * Props:
 * - children: Page content
 * - showSidebar: Boolean to show/hide sidebar
 * 
 * Usage:
 * <Layout showSidebar={true}>
 *   <YourPageContent />
 * </Layout>
 */

import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';

const Layout = ({ children, showSidebar = false }) => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <div className="flex flex-1">
        {showSidebar && <Sidebar />}
        
        <main className="flex-1 bg-gray-50">
          <div className="container mx-auto px-4 py-8">
            {children}
          </div>
        </main>
      </div>
      
      <Footer />
    </div>
  );
};

export default Layout;