import { Link, useNavigate } from "react-router-dom";
import { ToggleButton } from "./content/ToggleButton";

interface NavbarProps {
  isCandidateSearch: boolean;
  onToggle: () => void;
}

export function Navbar({ isCandidateSearch, onToggle }: NavbarProps) {
  const menus = ["Chat", "Cart"];
  const navigate = useNavigate();

  const handleLogout = () => {
    navigate("/login");
  };

  return (
    <nav className="bg-white text-black p-4 flex justify-between items-center h-20 shadow-md">
      {/* Logo & Menu Navigation */}
      <div className="flex items-center space-x-6">
        <img src="/assets/logo.png" className="h-8" alt="Logo" />
        <ul className="flex space-x-6 text-lg font-medium">
          {menus.map((item, index) => (
            <li key={index}>
              <Link
                to={`/admin/${item.toLowerCase()}`}
                className="hover:text-blue-500 transition duration-300"
              >
                {item}
              </Link>
            </li>
          ))}
        </ul>
        <ToggleButton isCandidateSearch={isCandidateSearch} onToggle={onToggle} />
      </div>

      {/* Logout Button */}
      <button
        onClick={handleLogout}
        className="bg-red-500 hover:bg-red-600 text-white px-5 py-2 rounded-lg transition duration-300"
      >
        Logout
      </button>
    </nav>
  );
}
