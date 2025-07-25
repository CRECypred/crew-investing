import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

import HomePage from "./pages/HomePage";
import StockPage from "./pages/StockPage";
import AnalizlerPage from "./pages/AnalizlerPage";
import ListelerPage from "./pages/ListelerPage";
import ProfilPage from "./pages/ProfilPage";
import IletisimPage from "./pages/IletisimPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import SignalListPage from "./pages/SignalListPage"; // 🆕 Eklendi
import Layout from "./components/Layout";
import FirstGroup from "./pages/FirstGroup";
import SecondGroup from "./pages/SecondGroup";
import ThirdGroup from "./pages/ThirdGroup";
import AdminPage from "./pages/AdminPage";

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem("darkMode");
    return saved === "true";
  });

  const toggleDarkMode = () => {
    setDarkMode((prev) => !prev);
  };

  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.classList.add("dark");
      localStorage.setItem("darkMode", "true");
    } else {
      root.classList.remove("dark");
      localStorage.setItem("darkMode", "false");
    }
  }, [darkMode]);

  return (
    <Router>
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-black dark:text-white transition-colors">

        {/* 🌙 Gece Modu Toggle Butonu */}
        <button
          onClick={toggleDarkMode}
          className="fixed top-4 right-4 z-50 bg-gray-200 dark:bg-gray-700 text-black dark:text-white px-3 py-2 rounded shadow"
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <Routes>
          <Route element={<Layout darkMode={darkMode} toggleDarkMode={toggleDarkMode} />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/stock/:symbol" element={<StockPage darkMode={darkMode} />} />
            <Route path="/analizler" element={<AnalizlerPage />} />
            <Route path="/listeler" element={<ListelerPage />} />
            <Route path="/listeler/:slug/:type" element={<SignalListPage />} /> {/* 🆕 Dinamik route */}
            <Route path="/profil" element={<ProfilPage />} />
            <Route path="/iletisim" element={<IletisimPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/listeler/ma" element={<FirstGroup />} />
            <Route path="/listeler/second" element={<SecondGroup />} />
            <Route path="/listeler/third" element={<ThirdGroup />} />
            <Route path="/admin" element={<AdminPage />} />

          </Route>
        </Routes>
      </div>
    </Router>
  );
}

export default App;
