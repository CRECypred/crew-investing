import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

// MACD, Trendline, MOST sinyalleri
const signalConfigs = [
  { slug: "macd-al", label: "MACD", url: "/api/macd-last-buy-signals", type: "macd", signalType: "al" },
  { slug: "macd-sat", label: "MACD", url: "/api/macd-last-sell-signals", type: "macd", signalType: "sat" },

  { slug: "trendline-al", label: "Trendline", url: "/api/trendline-last-buy-signals", type: "trendline", signalType: "al" },
  { slug: "trendline-sat", label: "Trendline", url: "/api/trendline-last-sell-signals", type: "trendline", signalType: "sat" },

  { slug: "most-al", label: "MOST", url: "/api/most-last-buy-signals", type: "most", signalType: "al" },
  { slug: "most-sat", label: "MOST", url: "/api/most-last-sell-signals", type: "most", signalType: "sat" },
];

const SecondGroup = () => {
  const [data, setData] = useState({});
  const [performance, setPerformance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      const allData = {};

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

      try {
        const [macdRes, trendRes, mostRes] = await Promise.all([
          fetch("/api/macd-performance"),
          fetch("/api/trendline-performance"),
          fetch("/api/most-performance"),
        ]);

        const macdJson = await macdRes.json();
        const trendJson = await trendRes.json();
        const mostJson = await mostRes.json();

        setPerformance([...macdJson, ...trendJson, ...mostJson]);
      } catch (e) {
        console.error("Error fetching performance", e);
      }

      setData(allData);
      setLoading(false);
    };

    fetchAll();
  }, []);

  const renderTable = (cfg) => {
    const list = Array.isArray(data[cfg.slug]) ? data[cfg.slug] : [];
    const limited = list.slice(0, 10);

    let listName = "";

    if (cfg.type === "macd") {
        listName = `${cfg.type}_${cfg.signalType}`;         // macd_al / macd_sat
    } else {
        listName = `${cfg.type}_${cfg.signalType === "al" ? "buy" : "sell"}`;  // trendline_buy / most_sell vs.
    }

    const perf = performance.find((p) => p.list_name === listName) || {};

    return (
      <section
        key={`${cfg.slug}`}
        className="mb-6 p-4 bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 w-full max-w-md"
      >
        <h2 className="text-md font-semibold mb-2 text-gray-700 dark:text-gray-200">
          {cfg.label} – {cfg.signalType.toUpperCase()} Sinyalleri
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
            <Link to={`/listeler/${cfg.slug}/${cfg.signalType}`} className="text-blue-500 text-sm hover:underline">
              Tümünü Gör →
            </Link>
          </div>
        )}
      </section>
    );
  };

  return (
    <div className="p-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <h1 className="text-2xl font-bold col-span-full mb-4">MACD, Trendline ve MOST Sinyalleri</h1>
      {loading ? (
        <p>Yükleniyor...</p>
      ) : (
        <>
          {signalConfigs.map((cfg) => renderTable(cfg))}
        </>
      )}
    </div>
  );
};

export default SecondGroup;
