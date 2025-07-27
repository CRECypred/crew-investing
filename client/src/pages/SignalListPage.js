import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const SignalListPage = () => {
  const { slug, type } = useParams();
  const [data, setData] = useState([]);

  // Dinamik endpoint oluştur
  const endpointMap = {
    // MA
    "ma-8-22": { name: "MA(8/22)", url: "/api/ma-last-signals-8-22" },
    "ma-22-50": { name: "MA(22/50)", url: "/api/ma-last-signals-22-50" },
    "ma-50-200": { name: "MA(50/200)", url: "/api/ma-last-signals-50-200" },

    // MACD
    "macd-al": { name: "MACD", url: "/api/macd-last-buy-signals" },
    "macd-sat": { name: "MACD", url: "/api/macd-last-sell-signals" },

    // Trendline
    "trendline-al": { name: "Trendline", url: "/api/trendline-last-buy-signals" },
    "trendline-sat": { name: "Trendline", url: "/api/trendline-last-sell-signals" },

    // ✅ MOST
  "most-al": { name: "MOST", url: "/api/most-last-buy-signals" },
  "most-sat": { name: "MOST", url: "/api/most-last-sell-signals" },

   //  MOST EMA
  "most-ema-al": { name: "MOST EMA", url: "/api/most-ema-last-buy-signals" },
  "most-ema-sat": { name: "MOST EMA", url: "/api/most-ema-last-sell-signals" },

  // ✅ Old School
  "oldschool-al": { name: "Old School", url: "/api/oldschool-last-buy-signals" },
  "oldschool-sat": { name: "Old School", url: "/api/oldschool-last-sell-signals" },
  };

  const config = endpointMap[`${slug}-${type?.toLowerCase()}`];

  useEffect(() => {
    if (!config) return;
    fetch(config.url)
      .then((res) => res.json())
      .then((all) => setData(all));
  }, [config]);

  if (!config) return <p className="p-6 text-red-500">Geçersiz liste türü.</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">
        {config.name} – {type.toUpperCase()} Sinyalleri
      </h1>

      <table className="min-w-full border text-sm text-center">
        <thead>
          <tr className="bg-gray-100 dark:bg-gray-700">
            <th className="border px-2 py-1">Sembol</th>
            <th className="border px-2 py-1">Tarih</th>
            <th className="border px-2 py-1">Sinyal Fiyatı</th>
            <th className="border px-2 py-1">Mevcut Fiyat</th>
            <th className="border px-2 py-1">% Değişim</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => {
            const change = item.change_percent;
            const changeClass =
              change > 0 ? "text-green-600"
              : change < 0 ? "text-red-600"
              : "";

            return (
              <tr key={item.symbol + item.date}>
                <td className="border px-2 py-1">{item.symbol}</td>
                <td className="border px-2 py-1">
                  {new Date(item.date).toLocaleDateString("tr-TR")}
                </td>
                <td className="border px-2 py-1">{item.signal_price?.toFixed(2) ?? "-"}</td>
                <td className="border px-2 py-1">{item.current_price?.toFixed(2) ?? "-"}</td>
                <td className={`border px-2 py-1 font-medium ${changeClass}`}>
                  {change != null ? `${change.toFixed(2)}%` : "-"}
                </td>
              </tr>
            );
          })}

          {data.length === 0 && (
            <tr>
              <td colSpan={5} className="text-center text-gray-500 py-2 italic">
                Veri bulunamadı
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default SignalListPage;
