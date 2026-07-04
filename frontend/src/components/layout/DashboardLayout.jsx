import Footer from "./Footer";
import Header from "./Header";
import Sidebar from "./Sidebar";

const DashboardLayout = ({ children, user, onLogout }) => {
  return (
    <div className="ds-ambient flex min-h-screen flex-col">
      <Header user={user} onLogout={onLogout} />
      <div className="flex flex-1">
        <Sidebar role={user?.role} />
        <main className="relative flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-48 ds-gradient-scrim" />
          <div className="relative">{children}</div>
        </main>
      </div>
      <Footer />
    </div>
  );
};

export default DashboardLayout;
