import Footer from "./Footer";
import Header from "./Header";
import Sidebar from "./Sidebar";

const DashboardLayout = ({ children, user, onLogout }) => {
  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ backgroundColor: "#DDD0C8" }}
    >
      <Header user={user} onLogout={onLogout} />
      <div className="flex flex-1">
        <Sidebar role={user?.role} />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 overflow-y-auto">
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default DashboardLayout;
