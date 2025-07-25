import React, { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Moon, Sun } from "lucide-react";

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [username, setUsername] = useState(null);
  const [role, setRole] = useState(null);
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("darkMode") === "true";
  });

  useEffect(() => {
    const storedUser = localStorage.getItem("username");
    const storedRole = localStorage.getItem("role");
    if (storedUser) setUsername(storedUser);
    if (storedRole) setRole(storedRole);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("darkMode", darkMode);
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode(!darkMode);

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("role");
    setUsername(null);
    setRole(null);
    window.location.reload();
  };

  return (
    <nav className="sticky top-0 z-50 shadow-md flex items-center justify-between border-b border-gray-300 py-6 px-8 text-14 font-open-sans text-blacks transition-all duration-300 hover:bg-blacks hover:text-white bg-white dark:bg-blacks dark:text-white">

      {/* Sol: Logo ve Site Adı (w-1/3) */}
      <div className="flex items-center space-x-3 w-1/3 cursor-pointer" onClick={() => navigate("/")}>
        <div className="relative w-14 h-14">
          <img
            src="/logo-default.png"
            alt="Crew Investing Logo"
            className="absolute inset-0 w-14 h-14 object-contain opacity-100 group-hover:opacity-0 transition-opacity duration-300"
          />
          <img
            src="/logo-hover.png"
            alt="Crew Investing Logo Hover"
            className="absolute inset-0 w-14 h-14 object-contain opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          />
        </div>
        <span className="text-2xl font-bold">Crew Investing</span>
      </div>

      {/* Orta: Menü (w-[42%]) */}
      <ul className="flex gap-6 justify-center w-[42%] whitespace-nowrap">
        {[
            { path: "/", label: "ANA SAYFA" },
            { path: "/analizler", label: "ANALİZLER" },
            { path: "/listeler", label: "LİSTELER" },
            { path: "/profil", label: "PROFİL" },
            { path: "/iletisim", label: "İLETİŞİM" },
        ].map((item) => (
            <li key={item.path}>
                <Link
                    to={item.path}
                    className={`font-bold text-lg transition duration-300 hover:underline whitespace-nowrap ${
                        location.pathname === item.path ? "border-b-2 border-black dark:border-white" : ""
                    }`}
                >
                    {item.label}
                </Link>
            </li>
        ))}

        {role === "admin" && (
            <li>
                <Link
                    to="/admin"
                    className={`font-bold text-lg text-red-600 dark:text-red-400 transition duration-300 hover:underline whitespace-nowrap ${
                        location.pathname === "/admin" ? "border-b-2 border-red-600 dark:border-red-400" : ""
                    }`}
                >
                    ADMIN
                </Link>
            </li>
        )}
      </ul>


      {/* Sağ: Dark mode + Avatar veya Giriş/Kayıt (w-1/4) */}
      <div className="w-1/4 flex justify-end items-center gap-4 relative">
        <button onClick={toggleDarkMode} className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition">
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        {username ? (
          <div className="relative group">
            <img
              src="https://i.pravatar.cc/40?u=crew-user"
              alt="Avatar"
              className="w-10 h-10 rounded-full cursor-pointer border-2 border-gray-300 group-hover:border-white transition"
            />
            <div className="absolute top-full right-0 mt-2 w-40 bg-white dark:bg-gray-800 text-black dark:text-white rounded shadow-lg opacity-0 group-hover:opacity-100 group-hover:pointer-events-auto transition-opacity duration-300 z-50">
              <ul className="py-1 text-sm">
                <li className="px-4 py-2 font-bold text-center border-b border-gray-300 dark:border-gray-600">
                  {username}
                  {role === "admin" && <span className="ml-2 text-xs bg-green-600 text-white px-2 py-0.5 rounded">CRE</span>}
                  {role === "mod" && <span className="ml-2 text-xs bg-gray-500 text-white px-2 py-0.5 rounded">MOD</span>}
                </li>
                <li className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">Ayarlar</li>
                <li
                  className="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                  onClick={handleLogout}
                >
                  Çıkış Yap
                </li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="flex gap-3">
            <button
              onClick={() => navigate("/login")}
              className="text-sm font-semibold hover:underline hover:text-blue-600"
            >
              Giriş Yap
            </button>
            <button
              onClick={() => navigate("/register")}
              className="text-sm font-semibold hover:underline hover:text-green-600"
            >
              Kayıt Ol
            </button>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
