import { Navbar } from "../components/Navbar/Navbar";
import { MainContent } from "../components/MainContent/MainContent";

export function AdminPage() {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Navbar */}
        <Navbar/>
        {/* Content Area */}
        <MainContent/>
      </div>
    </div>
  );
}
