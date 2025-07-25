import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

// Yalnızca MA sinyalleri
const signalConfigs = [
  { slug: "ma-8-22", label: "MA(8/22)", url: "/api/ma-last-signals-8-22", type: "ma" },
  { slug: "ma-22-50", label: "MA(22/50)", url: "/api/ma-last-signals-22-50", type: "ma" },
  { slug: "ma-50-200", label: "MA(50/200)", url: "/api/ma-last-signals-50-200", type: "ma" },
];

const FirstGroup = () => {
  const [data, setData] = useState({});
  const [performance, setPerformance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      const allData = {};

      // Sinyalleri çek
      for (const cfg of signalConfigs) {
        try {
          const res = await fetch(cfg.url);
          const json = await res.json();
          allData[cfg.slug] = json;
        } catch (e) {
          console.error(`Error fetching ${cfg.slug}`, e);
          allData[cfg.slug] = [];
        }
      }

      // Performans verisi
      try {
        const res = await fetch("/api/list-performance");
        const json = await res.json();
        setPerformance(json);
      } catch (e) {
        console.error("Error fetching performance", e);
      }

      setData(allData);
      setLoading(false);
    };

    fetchAll();
  }, []);

  const renderTable = (cfg, type) => {
    const list = Array.isArray(data[cfg.slug]) ? data[cfg.slug].filter(i => i.signal === type.toUpperCase()) : [];
    const limited = list.slice(0, 10);
    const [, sw, lw] = cfg.slug.split("-");
    const listName = `ma${sw}_${lw}_${type}`;

    const perf = performance.find((p) => p.list_name === listName) || {};

    return (
      <section key={`${cfg.slug}-${type}`} className="mb-6 p-4 bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 w-full max-w-md">
        <h2 className="text-md font-semibold mb-2 text-gray-700 dark:text-gray-200">
          {cfg.label} – {type.toUpperCase()} Sinyalleri
        </h2>

        {/* Hisse Listesi */}
        <div className="space-y-2 text-sm">
          {limited.map((item) => (
            <div key={item.symbol + item.date} className="flex flex-col px-2">
              <div className="flex justify-between font-medium">
                <span>{item.symbol}</span>
                <span className="text-gray-500 dark:text-gray-400">{item.date}</span>
              </div>
              <div className="text-xs text-gray-600 dark:text-gray-400 flex justify-between">
                <span>{item.signal_price} ₺ → {item.current_price} ₺</span>
                <span className={item.change_percent >= 0 ? "text-green-500" : "text-red-500"}>
                  ({item.change_percent}%)
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Performans */}
        <div className="mt-4 p-2 bg-gray-50 dark:bg-gray-700 rounded">
          <p className="text-sm text-gray-600 dark:text-gray-300">As of: {perf.as_of || "-"}</p>
          <ul className="mt-1 list-disc list-inside text-sm text-gray-700 dark:text-gray-200 space-y-1">
            <li>Günlük: {perf.daily != null ? `${(perf.daily * 100).toFixed(2)}%` : "-"}</li>
            <li>Haftalık: {perf.weekly != null ? `${(perf.weekly * 100).toFixed(2)}%` : "-"}</li>
            <li>Aylık: {perf.monthly != null ? `${(perf.monthly * 100).toFixed(2)}%` : "-"}</li>
            <li>Tüm Zamanlar: {perf.all_time != null ? `${(perf.all_time * 100).toFixed(2)}%` : "-"}</li>
          </ul>
        </div>

        {list.length > 10 && (
          <div className="mt-2 text-right">
            <Link to={`/listeler/${cfg.slug}/${type}`} className="text-blue-500 text-sm hover:underline">
              Tümünü Gör →
            </Link>
          </div>
        )}
      </section>
    );
  };

  return (
    <div className="p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <h1 className="text-2xl font-bold col-span-full mb-4">MA Sinyalleri</h1>
      {loading ? (
        <p>Yükleniyor...</p>
      ) : (
        <>
          {signalConfigs.flatMap((cfg) => ["al", "sat"].map((type) => renderTable(cfg, type)))}
        </>
      )}
    </div>
  );
};

export default FirstGroup;
