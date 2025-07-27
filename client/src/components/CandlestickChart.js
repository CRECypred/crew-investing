import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";
import { Sun, Moon } from "lucide-react";
import { Maximize, Minimize } from "lucide-react";
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;



const CandlestickChart = ({ symbol: initialSymbol, isDarkMode }) => {
  const chartRef = useRef(null);
  const containerRef = useRef(null);
  const supportRefs = useRef([]);
  const resistanceRefs = useRef([]);
  const ma8Ref = useRef(null);
  const ma22Ref = useRef(null);
  const ma22MidRef = useRef(null);
  const ma50MidRef = useRef(null);
  const ma50LongRef = useRef(null);
  const ma200LongRef = useRef(null);
  const mostRef = useRef(null);
  const maMostRef = useRef(null);
  const mostEMARef = useRef(null);
  const maGroupRef = useRef(null);
  const mostGroupRef = useRef(null);
  const mostButtonRef = useRef(null);
  const maButtonRef = useRef(null);





  const [symbol, setSymbol] = useState(initialSymbol);
  const [inputValue, setInputValue] = useState(initialSymbol);
  const [suggestions, setSuggestions] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);
  const listRef = useRef(null);


  const [showTrend, setShowTrend] = useState(false);
  const [showMA, setShowMA] = useState(false);
  const [showMA2, setShowMA2] = useState(false);
  const [showMA3, setShowMA3] = useState(false);
  const [showMOST, setShowMOST] = useState(false);
  const [showMostEMA, setShowMostEMA] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [localDarkMode, setLocalDarkMode] = useState(false);
  const [showMAGroup, setShowMAGroup] = useState(false);
  const [showMostGroup, setShowMostGroup] = useState(false);



  const [formattedCandles, setFormattedCandles] = useState([]);
  const [trendSegments, setTrendSegments] = useState([]);
  const [breakpoints, setBreakpoints] = useState([]);
  const [maData, setMaData] = useState({ ma8: [], ma22: [], signals: [] });
  const [maMidData, setMaMidData] = useState({ ma22: [], ma50: [], signals: [] });
  const [maLongData, setMaLongData] = useState({ ma50: [], ma200: [], signals: [] });
  const [mostData, setMostData] = useState([]);
  const [mostEMAData, setMostEMAData] = useState([]);
  const [hoveredData, setHoveredData] = useState(null);
  const [macdData, setMacdData] = useState([]);
  const [showMACD, setShowMACD] = useState(false);

  useEffect(() => {
  setSymbol(initialSymbol);
  setInputValue(initialSymbol);
  }, [initialSymbol]);

  useEffect(() => {
    if (inputValue.length < 2) return setSuggestions([]);
    const fetchSuggestions = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/symbols?q=${inputValue}`);
        const data = await res.json();
        setSuggestions(data);
      } catch (e) {
        console.error("Tahmin verisi alınamadı", e);
        setSuggestions([]);
      }
    };
    fetchSuggestions();
  }, [inputValue]);

  function deduplicateAndSort(data) {
    const seen = new Set();
    return data
        .sort((a, b) => a.time - b.time)
        .filter(d => {
            if (seen.has(d.time)) return false;
            seen.add(d.time);
            return true;
        });
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
        if (
            maGroupRef.current &&
            !maGroupRef.current.contains(event.target) &&
            maButtonRef.current &&
            !maButtonRef.current.contains(event.target)
        ) {
            setShowMAGroup(false);
        }
    };

    if (showMAGroup) {
        document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
        document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showMAGroup]);

  useEffect(() => {
  const handleClickOutside = (e) => {
    if (
      inputRef.current &&
      !inputRef.current.contains(e.target) &&
      listRef.current &&
      !listRef.current.contains(e.target)
    ) {
      setSuggestions([]);
    }
  };

  document.addEventListener("mousedown", handleClickOutside);
  return () => document.removeEventListener("mousedown", handleClickOutside);
}, []);


  useEffect(() => {
    const handleClickOutside = (event) => {
        if (
            mostGroupRef.current &&
            !mostGroupRef.current.contains(event.target) &&
            mostButtonRef.current &&
            !mostButtonRef.current.contains(event.target)
        ) {
            setShowMostGroup(false);
        }
    };

    if (showMostGroup) {
        document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
        document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [showMostGroup]);



  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const candleRes = await fetch(`${BACKEND_URL}/api/chart/${symbol}`);
        const candleData = await candleRes.json();
        if (!Array.isArray(candleData)) throw new Error("Veri formatı hatalı");

        const candles = candleData.map((item) => ({
          time: Math.floor(new Date(item.time).getTime() / 1000),
          open: item.open,
          high: item.high,
          low: item.low,
          close: item.close,
        }));
        setFormattedCandles(candles);

        const trendRes = await fetch(`${BACKEND_URL}/api/trendlines/${symbol}`);
        const trendData = await trendRes.json();
        setTrendSegments(trendData.segments || []);
        setBreakpoints(trendData.breaks || []);

        const maRes = await fetch(`${BACKEND_URL}/api/ma-signals/${symbol}`);
        setMaData(await maRes.json());

        const maMidRes = await fetch(`${BACKEND_URL}/api/ma-midsignals/${symbol}`);
        setMaMidData(await maMidRes.json());

        const maLongRes = await fetch(`${BACKEND_URL}/api/ma-signals-50-200/${symbol}`);
        setMaLongData(await maLongRes.json());

        const mostRes = await fetch(`${BACKEND_URL}/api/most/${symbol}`);
        setMostData(await mostRes.json());

        const macdRes = await fetch(`${BACKEND_URL}/api/macd/${symbol}`);
        setMacdData(await macdRes.json());


        setLoading(false);
      } catch (err) {
        console.error("Grafik verisi alınamadı:", err);
        setError("Grafik verisi alınamadı.");
        setLoading(false);
      }
    };

    fetchData();
  }, [symbol]);

  useEffect(() => {
    const handleKeyDown = (e) => {
        if (e.key === "Escape") setIsFullscreen(false);
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (!showMostEMA) {
      setMostEMAData([]);
      return;
    }

    const fetchMostEMA = async () => {
      try {
        const response = await fetch(`${BACKEND_URL}/api/most-ema/${symbol}`);
        const data = await response.json();
        if (!Array.isArray(data)) return;
        setMostEMAData(data);
      } catch (error) {
        console.error("MOST EMA verisi çekilemedi:", error);
      }
    };

    fetchMostEMA();
  }, [showMostEMA, symbol]);

  useEffect(() => {
    if (loading || error || formattedCandles.length === 0 || !containerRef.current) return;

  // 🔁 Önceki grafik varsa temizle
    if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
    }

  // 🧹 HTML temizliği


  // 🎨 Grafik oluşturuluyor
    const chart = createChart(containerRef.current, {
        width: containerRef.current.clientWidth,
        height: 800,
        layout: {
            background: { color: localDarkMode ? "#1e1e1e" : "#ffffff" },
            textColor: localDarkMode ? "#e0e0e0" : "#000000",
        },
        grid: {
            vertLines: { color: localDarkMode ? "#444444" : "#eeeeee" },
            horzLines: { color: localDarkMode ? "#444444" : "#eeeeee" },
        },
        timeScale: { minBarSpacing: 0.5 },
    });

    const candleSeries = chart.addCandlestickSeries();
    candleSeries.setData(deduplicateAndSort(formattedCandles));

    const resizeChart = () => {
        chart.applyOptions({
            width: containerRef.current.clientWidth,
            height: containerRef.current.clientHeight,
        });
    };
    resizeChart();
    window.addEventListener("resize", resizeChart);

    if (showMACD && macdData.length > 0) {
        const macdLine = chart.addLineSeries({ color: "orange", lineWidth: 2 });
        const signalLine = chart.addLineSeries({ color: "blue", lineWidth: 2 });

        const histogramSeries = chart.addHistogramSeries({
            base: 0,
            priceLineVisible: false,
            lineWidth: 1
        });

        const macdPoints = deduplicateAndSort(macdData
            .filter(d => d.macd !== null)
            .map(d => ({
                time: new Date(d.time).toISOString().slice(0, 10),
                value: d.macd,
            }))
        );

        const signalPoints = deduplicateAndSort(macdData
            .filter(d => d.signal !== null)
            .map(d => ({
              time: new Date(d.time).toISOString().slice(0, 10),
                value: d.signal,
            }))
        );

        const histogramPoints = deduplicateAndSort(macdData
            .filter(d => d.hist !== null)
            .map(d => ({
                time: new Date(d.time).toISOString().slice(0, 10),
                value: d.hist,
                color: d.hist >= 0 ? "green" : "red"
            }))
        );

        macdLine.setData(macdPoints);
        signalLine.setData(signalPoints);
        histogramSeries.setData(histogramPoints);


        const macdMarkers = macdData
            .filter(d => d.signal_type)
            .map(d => ({
                time: Math.floor(new Date(d.time).getTime() / 1000),
                position: d.signal_type === "buy" ? "belowBar" : "aboveBar",
                color: d.signal_type === "buy" ? "green" : "red",
                shape: d.signal_type === "buy" ? "arrowUp" : "arrowDown",
                text: `MACD ${d.signal_type.toUpperCase()}`
            }));

        macdLine.setMarkers(macdMarkers);
    }


    if (showTrend) {
      trendSegments.forEach((segment) => {
        const dates = segment.dates;
        const support = segment.support;
        const resistance = segment.resistance;

        const supportSeries = chart.addLineSeries({
          color: "green", lineWidth: 3, lineStyle: 2,
          priceLineVisible: false, lastValueVisible: false
        });
        const resistanceSeries = chart.addLineSeries({
          color: "red", lineWidth: 3, lineStyle: 2,
          priceLineVisible: false, lastValueVisible: false
        });

        supportSeries.setData(
            deduplicateAndSort(
                dates.map((d, i) => ({
                    time: Math.floor(new Date(d).getTime() / 1000),
                    value: support[i],
                }))
            )
        );

        resistanceSeries.setData(
            deduplicateAndSort(
                dates.map((d, i) => ({
                    time: Math.floor(new Date(d).getTime() / 1000),
                    value: resistance[i],
                }))
            )
        );


        supportRefs.current.push(supportSeries);
        resistanceRefs.current.push(resistanceSeries);
      });
    }

    if (showMA) {
      ma8Ref.current = chart.addLineSeries({ color: "orange", lineWidth: 2 });
      ma22Ref.current = chart.addLineSeries({ color: "purple", lineWidth: 2 });

      ma8Ref.current.setData(
        deduplicateAndSort(
            maData.ma8.map((p) => ({
                time: Math.floor(new Date(p.date).getTime() / 1000),
                value: p.value,
            }))
        )
      );

      ma22Ref.current.setData(
        deduplicateAndSort(
            maData.ma22.map((p) => ({
                time: Math.floor(new Date(p.date).getTime() / 1000),
                value: p.value,
            }))
        )
      );
    }

    if (showMA2) {
      ma22MidRef.current = chart.addLineSeries({ color: "brown", lineWidth: 2 });
      ma50MidRef.current = chart.addLineSeries({ color: "blue", lineWidth: 2 });

      ma22MidRef.current.setData(
        deduplicateAndSort(
            maMidData.ma22.map((p) => ({
                time: Math.floor(new Date(p.date).getTime() / 1000),
                value: p.value,
            }))
        )
      );

      ma50MidRef.current.setData(
        deduplicateAndSort(
            maMidData.ma50.map((p) => ({
                time: Math.floor(new Date(p.date).getTime() / 1000),
                value: p.value,
            }))
        )
      );
    }

    if (showMA3) {
      ma50LongRef.current = chart.addLineSeries({ color: "darkorange", lineWidth: 2 });
      ma200LongRef.current = chart.addLineSeries({ color: "darkblue", lineWidth: 2 });

      ma50LongRef.current.setData(
        deduplicateAndSort(
            maLongData.ma50.map((p) => ({
                time: Math.floor(new Date(p.date).getTime() / 1000),
                value: p.value,
            }))
        )
      );

      ma200LongRef.current.setData(
        deduplicateAndSort(
            maLongData.ma200.map((p) => ({
                time: Math.floor(new Date(p.date).getTime() / 1000),
                value: p.value,
            }))
        )
      );
    }

    if (showMOST && mostData.length > 0) {
      const mostSeries = chart.addLineSeries({ color: "black", lineWidth: 2 });
      const maSeries = chart.addLineSeries({ color: "gray", lineWidth: 1, lineStyle: 2 });

      mostRef.current = mostSeries;
      maMostRef.current = maSeries;

      mostSeries.setData(
        deduplicateAndSort(
            mostData.filter(p => p.most !== null).map(p => ({
                time: Math.floor(new Date(p.time).getTime() / 1000),
                value: p.most,
            }))
        )
      );

      maSeries.setData(
        deduplicateAndSort(
            mostData.filter(p => p.ma !== null).map(p => ({
                time: Math.floor(new Date(p.time).getTime() / 1000),
                value: p.ma,
            }))
        )
      );
    }

    if (showMostEMA && mostEMAData.length > 0) {
      const emaSeries = chart.addLineSeries({
        color: 'blue',
        lineWidth: 1,
        priceLineVisible: false,
      });
      mostEMARef.current = emaSeries;

      const formatted = mostEMAData
        .filter(d => d.most !== null)
        .map(d => ({
          time: Math.floor(new Date(d.time).getTime() / 1000),
          value: d.most
        }))
        .sort((a, b) => a.time - b.time);

      const uniqueFormatted = [];
      const seenTimes = new Set();
      for (const item of formatted) {
        if (!seenTimes.has(item.time)) {
          uniqueFormatted.push(item);
          seenTimes.add(item.time);
        }
      }

      emaSeries.setData(uniqueFormatted);

      const markers = mostEMAData
        .filter(d => d.signal)
        .map(d => ({
          time: Math.floor(new Date(d.time).getTime() / 1000),
          position: d.signal === "buy" ? "belowBar" : "aboveBar",
          color: d.signal === "buy" ? "blue" : "orange",
          shape: d.signal === "buy" ? "arrowUp" : "arrowDown",
          text: `EMA ${d.signal.toUpperCase()}`
        }))
        .sort((a, b) => a.time - b.time);

      if (markers.length > 0) {
        emaSeries.setMarkers(markers);
      }
    }

    const allMarkers = [];

    if (showTrend) {
      allMarkers.push(...breakpoints.map((bp) => ({
        time: Math.floor(new Date(bp.date).getTime() / 1000),
        position: bp.type === "BUY" ? "belowBar" : "aboveBar",
        color: bp.type === "BUY" ? "green" : "red",
        shape: bp.type === "BUY" ? "arrowUp" : "arrowDown",
        text: `${bp.type} @ ${bp.price}`,
      })));
    }

    if (showMA) {
      allMarkers.push(...maData.signals.map((bp) => ({
        time: Math.floor(new Date(bp.date).getTime() / 1000),
        position: bp.type === "BUY" ? "belowBar" : "aboveBar",
        color: bp.type === "BUY" ? "blue" : "orange",
        shape: bp.type === "BUY" ? "arrowUp" : "arrowDown",
        text: `MA ${bp.type}`,
      })));
    }

    if (showMA2) {
      allMarkers.push(...maMidData.signals.map((bp) => ({
        time: Math.floor(new Date(bp.date).getTime() / 1000),
        position: bp.type === "BUY" ? "belowBar" : "aboveBar",
        color: bp.type === "BUY" ? "darkblue" : "brown",
        shape: bp.type === "BUY" ? "arrowUp" : "arrowDown",
        text: `Mid ${bp.type}`,
      })));
    }

    if (showMA3) {
      allMarkers.push(...maLongData.signals.map((bp) => ({
        time: Math.floor(new Date(bp.date).getTime() / 1000),
        position: bp.type === "BUY" ? "belowBar" : "aboveBar",
        color: bp.type === "BUY" ? "green" : "red",
        shape: bp.type === "BUY" ? "arrowUp" : "arrowDown",
        text: `Long ${bp.type}`,
      })));
    }

    if (showMOST) {
      allMarkers.push(...mostData
        .filter(p => p.signal)
        .map(p => ({
          time: Math.floor(new Date(p.time).getTime() / 1000),
          position: p.signal === "buy" ? "belowBar" : "aboveBar",
          color: p.signal === "buy" ? "green" : "red",
          shape: p.signal === "buy" ? "arrowUp" : "arrowDown",
          text: `MOST ${p.signal.toUpperCase()}`
        }))
      );
    }

    allMarkers.sort((a, b) => a.time - b.time);
    candleSeries.setMarkers(allMarkers);

    chart.timeScale().fitContent();
    chart.subscribeCrosshairMove(param => {
        if (!param || !param.time || !param.seriesData) {
            setHoveredData(null);
            return;
        }

        const time = param.time;
        const candle = param.seriesData.get(candleSeries);

        if (candle) {
            setHoveredData({
                time,
                open: candle.open,
                  high: candle.high,
                  low: candle.low,
                  close: candle.close,
            });
        } else {
          setHoveredData(null);
        }
    });

    chartRef.current = chart;

  return () => {
    if (chartRef.current) chartRef.current.remove();
    chartRef.current = null;
    supportRefs.current = [];
    resistanceRefs.current = [];
    window.removeEventListener("resize", resizeChart);
  };
}, [
  formattedCandles, trendSegments, breakpoints,
  maData, maMidData, maLongData,
  mostData, mostEMAData,
  showTrend, showMA, showMA2, showMA3, showMOST, showMostEMA,
  isFullscreen, symbol, localDarkMode, showMACD, loading, error, macdData
]);



  return (
    <div className={`p-4 rounded-xl shadow transition-colors
        ${isFullscreen
           ? (localDarkMode ? "fixed inset-0 z-50 bg-gray-900 text-white" : "fixed inset-0 z-50 bg-white text-black")
           : (localDarkMode ? "bg-gray-800 text-white" : "bg-white text-black")}
    `}>
        <div className="flex flex-wrap justify-between items-center mb-2 space-x-2">
        <div className="flex items-center space-x-2 relative">
          <span className="text-xl font-bold">Hisse Grafiği:</span>
          <div className="relative">
            <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter") {
                        let newSymbol = inputValue.trim().toUpperCase();
                        if (!newSymbol.includes(".") && !newSymbol.includes("=")) {
                            newSymbol += ".IS";
                        }
                        setSymbol(newSymbol);
                        setSuggestions([]);
                    }
                }}
                className={`border rounded px-2 py-1 text-sm w-32 transition-colors duration-200
                    ${localDarkMode ? "bg-gray-800 text-white border-gray-600 placeholder-gray-400" : "bg-white text-black border-gray-300 placeholder-gray-500"}
                `}
                placeholder="THYAO.IS"
            />
            {suggestions.length > 0 && (
              <ul
                ref={listRef}
                className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded shadow text-left text-sm max-h-52 overflow-y-auto"
              >
                {suggestions.map((s, i) => (
                  <li
                    key={i}
                    onClick={() => {
                      setInputValue(s);
                      setSymbol(s);
                      setSuggestions([]);
                    }}
                    className="px-2 py-1 hover:bg-gray-100 cursor-pointer"
                  >
                    {s}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        <div className="space-x-2 flex flex-wrap">
            <button onClick={() => setShowTrend(p => !p)} className="px-3 py-1 bg-blue-500 text-white rounded">Trend</button>
            {/* MOST Grubu Butonu */}
            <div className="relative inline-block">
                <button
                    ref={mostButtonRef}
                    onClick={() => setShowMostGroup(prev => !prev)}
                    className="px-3 py-1 bg-green-700 text-white rounded hover:bg-green-800"
                >
                    MOST
                </button>
                {showMostGroup && (
                    <div
                        ref={mostGroupRef}
                        className="absolute left-0 mt-2 flex gap-2 bg-white dark:bg-gray-500 border border-gray-300 dark:border-gray-600 rounded p-2 shadow z-20 whitespace-nowrap"
                    >
                        <button
                            onClick={() => setShowMOST(p => !p)}
                            className="px-3 py-1 bg-green-400 text-white rounded hover:bg-green-500 text-sm"
                        >
                            VAR
                        </button>
                        <button
                            onClick={() => setShowMostEMA(p => !p)}
                            className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                        >
                            EMA
                        </button>
                    </div>
                )}
            </div>


            {/* MA Grubu Butonu */}
            <div className="relative inline-block">
                <button
                    ref={maButtonRef}
                    onClick={() => setShowMAGroup(prev => !prev)}
                    className="px-3 py-1 bg-yellow-500 text-white rounded"
                >
                    MA
                </button>
                {showMAGroup && (
                    <div
                        ref={maGroupRef}
                        className="absolute left-0 mt-2 flex gap-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded p-2 shadow z-20 whitespace-nowrap"
                    >

                        <button
                            onClick={() => setShowMA(p => !p)}
                            className="px-3 py-1 bg-yellow-400 text-white rounded hover:bg-cyan-600 text-sm"
                        >
                            9/22 MA
                        </button>
                        <button
                            onClick={() => setShowMA2(p => !p)}
                            className="px-3 py-1 bg-yellow-500 text-white rounded hover:bg-sky-600 text-sm"
                        >
                            22/50 MA
                        </button>
                        <button
                            onClick={() => setShowMA3(p => !p)}
                            className="px-3 py-1 bg-yellow-600 text-white rounded hover:bg-blue-600 text-sm"
                        >
                            50/200 MA
                        </button>
                    </div>
                )}
  </div>


  <button onClick={() => setShowMACD(p => !p)} className="px-3 py-1 bg-red-600 text-white rounded">MACD</button>

  <button
    onClick={() => setIsFullscreen(p => !p)}
    className="p-2 rounded hover:opacity-90 transition bg-gray-600 text-white"
    title={isFullscreen ? "Tam Ekrandan Çık" : "Tam Ekran"}
  >
    {isFullscreen ? <Minimize size={18} /> : <Maximize size={18} />}
  </button>

  <button
    onClick={() => setLocalDarkMode(prev => !prev)}
    className="p-2 bg-gray-600 text-white rounded hover:bg-gray-700"
    title={localDarkMode ? "Aydınlık Grafik" : "Karanlık Grafik"}
  >
    {localDarkMode ? <Sun size={18} /> : <Moon size={18} />}
  </button>
</div>
      </div>

     {loading && <p className="text-gray-500">Yükleniyor...</p>}
    {error && <p className="text-red-600">{error}</p>}

    <div
      ref={containerRef}
      className={`relative w-full ${isFullscreen ? "h-[calc(100vh-100px)]" : "h-[500px]"}`}
    >
      {hoveredData && (
        <div className={`absolute top-2 left-2 p-2 text-sm rounded z-50 border shadow
          ${isDarkMode ? "bg-gray-800 text-white border-gray-600" : "bg-white text-black border-gray-300"}
        `}>
          <div><strong>Tarih:</strong> {new Date(hoveredData.time * 1000).toLocaleDateString()}</div>
          <div><strong>Açılış:</strong> {hoveredData.open}</div>
          <div><strong>Yüksek:</strong> {hoveredData.high}</div>
          <div><strong>Düşük:</strong> {hoveredData.low}</div>
          <div><strong>Kapanış:</strong> {hoveredData.close}</div>
        </div>
      )}
    </div>
  </div>
);
};

export default CandlestickChart;
