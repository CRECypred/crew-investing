import React, { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import SearchBar from "../components/SearchBar";
import CandlestickChart from "../components/CandlestickChart";
import CommentSection from "../components/CommentSection";

const StockPage = ({ darkMode }) => {
  const { symbol } = useParams();
  const selectedSymbol = symbol ? symbol.toUpperCase() : "XU100.IS";

  const [summary, setSummary] = useState(null);
  const [fundamentals, setFundamentals] = useState([]);
  const [flashClass, setFlashClass] = useState("");
  const [lastUpdateTime, setLastUpdateTime] = useState(null);
  const [techScore, setTechScore] = useState(0);
  const [techSignals, setTechSignals] = useState({
    short: null,
    medium: null,
    long: null,
    macd: null,
    most: null,
  });

  const previousPriceRef = useRef(null);

  const calculateScoreFromSignals = (signals) => {
    let score = 0;
    if (signals.short === "AL") score += 1;
    else if (signals.short === "SAT") score -= 1;
    if (signals.medium === "AL") score += 1;
    else if (signals.medium === "SAT") score -= 1;
    if (signals.long === "AL") score += 1;
    else if (signals.long === "SAT") score -= 1;
    if (signals.macd === "AL") score += 3;
    else if (signals.macd === "SAT") score -= 3;
    if (signals.most === "AL") score += 5;
    else if (signals.most === "SAT") score -= 5;
    return score;
  };

  useEffect(() => {
    const fetchSummary = () => {
      fetch(`/api/summary/${selectedSymbol}`)
        .then((res) => res.json())
        .then((data) => {
          const prev = previousPriceRef.current;
          if (prev !== null && prev !== data.price) {
            if (data.price > prev) {
              setFlashClass("flash-green");
            } else if (data.price < prev) {
              setFlashClass("flash-red");
            }
            setTimeout(() => setFlashClass(""), 700);
          }
          previousPriceRef.current = data.price;
          setSummary(data);
          setLastUpdateTime(new Date());
        })
        .catch((err) => console.error("Özet veri hatası:", err));
    };
    fetchSummary();
    const interval = setInterval(fetchSummary, 30000);
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  useEffect(() => {
    fetch(`/api/list-status/${selectedSymbol}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.statuses) {
          const s = data.statuses;
          const updatedSignals = {
            short: s.ma_8_22 === "buy" ? "AL" : s.ma_8_22 === "sell" ? "SAT" : null,
            medium: s.ma_22_50 === "buy" ? "AL" : s.ma_22_50 === "sell" ? "SAT" : null,
            long: s.ma_50_200 === "buy" ? "AL" : s.ma_50_200 === "sell" ? "SAT" : null,
            macd: s.macd === "buy" ? "AL" : s.macd === "sell" ? "SAT" : null,
            most: s.most_ema === "buy" ? "AL" : s.most_ema === "sell" ? "SAT" : null,
          };
          setTechSignals(updatedSignals);
          const score = calculateScoreFromSignals(updatedSignals);
          setTechScore(score);
        }
      })
      .catch((err) => console.error("list-status hatası:", err));
  }, [selectedSymbol]);

  useEffect(() => {
    fetch(`/api/fundamentals/${selectedSymbol}`)
      .then((res) => res.json())
      .then((data) => setFundamentals(data))
      .catch((err) => console.error("Temel veri hatası:", err));
  }, [selectedSymbol]);

  const formatNumberReadable = (num) => {
    if (typeof num !== "number") return num;
    if (num >= 1e9) return (num / 1e9).toFixed(2) + " Milyar";
    if (num >= 1e6) return (num / 1e6).toFixed(2) + " Milyon";
    if (num >= 1e3) return (num / 1e3).toFixed(2) + " Bin";
    return num.toLocaleString("tr-TR");
  };

  const renderScoreBar = () => (
    <div className="w-60 mt-2 mb-2 flex flex-col items-center">
      <h2 className="text-md font-semibold mb-1">Teknik Skor</h2>
      <div className="w-full h-3 bg-gray-300 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-300 ${
            techScore > 6
              ? "bg-green-600"
              : techScore > 2
              ? "bg-green-400"
              : techScore > -2
              ? "bg-yellow-400"
              : techScore > -6
              ? "bg-red-400"
              : "bg-red-600"
          }`}
          style={{ width: `${((techScore + 11) / 22) * 100}%` }}
        ></div>
      </div>
      <p className="text-xs text-gray-500 mt-1 italic">
        Puan: {techScore} – {techScore >= 6 ? "Güçlü AL" : techScore >= 2 ? "AL" : techScore >= -2 ? "Nötr" : techScore >= -6 ? "SAT" : "Güçlü SAT"}
      </p>
      <div className="text-xs text-center mt-2 text-gray-600 dark:text-gray-300 space-y-1">
        <div>MA(8/22): {techSignals.short || "–"}</div>
        <div>MA(22/50): {techSignals.medium || "–"}</div>
        <div>MA(50/200): {techSignals.long || "–"}</div>
        <div>MACD: {techSignals.macd || "–"}</div>
        <div>MOST EMA: {techSignals.most || "–"}</div>
      </div>
    </div>
  );

  return (
    <div className="relative p-8 font-open-sans min-h-screen bg-gray-100 dark:bg-gray-900 text-black dark:text-white transition-colors">
      <style>
        {`
          .flash-green { animation: flashGreen 1.0s ease-in-out; }
          .flash-red { animation: flashRed 1.0s ease-in-out; }
          @keyframes flashGreen {
            0% { background-color: #c6f6d5; }
            100% { background-color: transparent; }
          }
          @keyframes flashRed {
            0% { background-color: #fed7d7; }
            100% { background-color: transparent; }
          }
        `}
      </style>

      <div className="flex flex-col md:flex-row md:items-start md:justify-between mb-8">
        <div className="space-y-2">
          <div className="flex items-center gap-4">
            <h1 className="text-4xl font-bold tracking-tight">
              {summary?.name || selectedSymbol}
            </h1>
            <p className="text-md text-gray-500 dark:text-gray-400 font-mono">
              {selectedSymbol}
            </p>
          </div>

          {summary && (
            <div className="flex flex-col gap-2 mt-2">
              <div className="flex flex-wrap items-center gap-6">
                <p className={`text-3xl font-semibold ${flashClass}`}>
                  {summary.price} {summary.currency}
                </p>
                <p className={`text-xl font-bold flex items-center gap-2 ${
                  summary.changePercent >= 0 ? "text-green-500" : "text-red-500"}`}>
                  {summary.changePercent >= 0 ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownRight className="w-5 h-5" />}
                  {summary.changePercent > 0 ? "+" : ""}
                  {summary.changePercent.toFixed(2)}%
                  ({summary.changeAmount > 0 ? "+" : ""}
                  {summary.changeAmount.toFixed(2)} {summary.currency})
                </p>
              </div>
              {lastUpdateTime && (
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Son güncelleme: {lastUpdateTime.toLocaleTimeString("tr-TR")}
                  </p>
                  <p className="text-sm italic text-gray-400 dark:text-gray-500">
                    Veriler 15 dakika gecikmelidir
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="my-4 md:my-0">
          <SearchBar />
        </div>

        {summary && (
          <div className="flex flex-col md:items-end items-start gap-3 ml-4">
            <div className="text-sm text-gray-600 dark:text-gray-300 bg-white/70 dark:bg-gray-800/70 backdrop-blur-md px-4 py-3 rounded-xl shadow-md space-y-1 mt-4 md:mt-0">
              <p><span className="font-semibold">Sektör:</span> {summary.sector}</p>
              <p><span className="font-semibold">Hacim:</span> {summary.volume.toLocaleString("tr-TR")}</p>
              <p><span className="font-semibold">Kapanış Saati:</span> {summary.closeTime}</p>
            </div>
            {renderScoreBar()}
          </div>
        )}
      </div>

      <div className="relative w-full max-w-screen-xl ml-0 mr-auto">
        <CandlestickChart symbol={selectedSymbol} isDarkMode={darkMode} />
      </div>

      {fundamentals.length > 0 && (
        <div className="mt-10">
          <h2 className="text-2xl font-semibold mb-4">Temel Finansal Bilgiler</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {fundamentals.map((item) => (
              <div key={item.key} className="bg-white dark:bg-gray-800 p-4 rounded-xl shadow text-center">
                <p className="text-sm text-gray-500 dark:text-gray-400">{item.label}</p>
                <p className="text-lg font-bold mt-1">
                  {(item.key === "netIncome" || item.key === "revenue") &&
                  typeof item.value === "number" && !isNaN(item.value)
                    ? `${formatNumberReadable(item.value)} TRY`
                    : typeof item.value === "number" && !isNaN(item.value)
                    ? item.value.toFixed(2)
                    : item.value}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <CommentSection symbol={selectedSymbol} />
    </div>
  );
};

export default StockPage;
