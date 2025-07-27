import { useEffect, useState } from "react";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import CandlestickChart from "../components/CandlestickChart";
import SearchBar from "../components/SearchBar"; // ✅ yeni eklenen bileşen
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function HomePage() {
  const [prices, setPrices] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const navigate = useNavigate();

  const fetchPrices = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/prices)`);
      const data = await response.json();
      setPrices(data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      console.error("Veri çekme hatası:", error);
    }
  };

  useEffect(() => {
    fetchPrices();
    const interval = setInterval(fetchPrices, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleSelectSymbol = (symbol) => {
    let sym = symbol.toUpperCase();
    if (!sym.includes(".") && !sym.includes("=")) {
      sym += ".IS";
    }
    navigate(`/stock/${sym}`);
  };

  return (
    <div className="p-8 font-open-sans bg-gray-100 dark:bg-neutral-900 text-black dark:text-white min-h-screen">
      <h2 className="text-xl font-semibold text-center mt-8 mb-4">Güncel Piyasa Verileri</h2>

      <div className="flex flex-wrap gap-6 justify-center mb-10">
        {prices.map((item) => {
          const isPositive = item.change >= 0;
          return (
            <div
              key={item.symbol}
              className="w-64 p-4 rounded-xl shadow bg-white dark:bg-neutral-800 border-l-4 flex justify-between items-center transition-transform duration-200 hover:shadow-lg hover:-translate-y-1 hover:bg-gray-50 dark:hover:bg-neutral-700"
              style={{ borderColor: isPositive ? "green" : "red" }}
              onClick={() => handleSelectSymbol(item.symbol)}
            >
              <div>
                <div className="text-lg font-bold">{item.name}</div>
                <div className="text-sm text-gray-600 dark:text-gray-300">Açılış: {item.open}</div>
                <div className="text-sm text-gray-800 dark:text-gray-200">Anlık: {item.current}</div>
                <div className={`text-sm font-semibold ${isPositive ? "text-green-600" : "text-red-600"}`}>
                  {isPositive ? "+" : ""}
                  {item.change.toFixed(2)} ({item.change_percent.toFixed(2)}%)
                </div>
              </div>
              <div className="text-3xl text-gray-400 flex items-center justify-center h-full pl-2">
                {isPositive ? <ArrowUpRight className="text-green-600" /> : <ArrowDownRight className="text-red-600" />}
              </div>
            </div>
          );
        })}
      </div>

      {/* ✅ Yeni: Arama kutusu bileşeni */}
      <SearchBar />

      <h2 className="text-xl font-semibold mb-4 text-left">Grafik</h2>
      <div className="w-full px-4 ml-0 text-left">
        <CandlestickChart
          symbol="XU100.IS"
          darkMode={document.documentElement.classList.contains("dark")}
        />
      </div>
    </div>
  );
}

export default HomePage;
