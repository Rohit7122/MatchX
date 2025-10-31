import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useEffect, useState } from 'react';

interface Trade {
  trade_id: string;
  price: string;
  quantity: string;
  timestamp: string;
  aggressor_side: string;
}

interface PriceChartProps {
  trades: Trade[];
  symbol: string;
}

export function PriceChart({ trades, symbol }: PriceChartProps) {
  const [chartData, setChartData] = useState<any[]>([]);
  const [stats, setStats] = useState({
    high: 0,
    low: 0,
    volume: 0,
    change: 0
  });

  useEffect(() => {
    if (trades.length === 0) return;

    // Aggregate trades into time buckets (1 minute)
    const buckets = new Map<string, { price: number; volume: number; count: number }>();
    
    trades.forEach(trade => {
      const date = new Date(trade.timestamp);
      const bucket = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 
                              date.getHours(), date.getMinutes()).getTime();
      
      const price = parseFloat(trade.price);
      const qty = parseFloat(trade.quantity);
      
      if (!buckets.has(bucket.toString())) {
        buckets.set(bucket.toString(), { price: 0, volume: 0, count: 0 });
      }
      
      const data = buckets.get(bucket.toString())!;
      data.price += price;
      data.volume += qty;
      data.count += 1;
    });

    // Convert to chart data
    const data = Array.from(buckets.entries())
      .map(([time, data]) => ({
        time: parseInt(time),
        price: data.price / data.count,
        volume: data.volume
      }))
      .sort((a, b) => a.time - b.time)
      .slice(-30); // Last 30 minutes

    setChartData(data);

    // Calculate stats
    if (trades.length > 0) {
      const prices = trades.map(t => parseFloat(t.price));
      const high = Math.max(...prices);
      const low = Math.min(...prices);
      const volume = trades.reduce((sum, t) => sum + parseFloat(t.quantity), 0);
      const firstPrice = parseFloat(trades[trades.length - 1].price);
      const lastPrice = parseFloat(trades[0].price);
      const change = ((lastPrice - firstPrice) / firstPrice) * 100;

      setStats({ high, low, volume, change });
    }
  }, [trades]);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const date = new Date(data.time);
      
      return (
        <div className="bg-dark-elevated border border-dark-border rounded-lg p-3 shadow-xl">
          <p className="text-xs text-text-muted mb-1">
            {date.toLocaleTimeString()}
          </p>
          <p className="text-sm font-semibold text-accent-green">
            ${data.price.toFixed(2)}
          </p>
          <p className="text-xs text-text-secondary">
            Vol: {data.volume.toFixed(4)}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-dark-surface rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">{symbol} Price Chart</h2>
        
        {/* Stats */}
        <div className="flex items-center space-x-6 text-sm">
          <div>
            <span className="text-text-muted">24h High:</span>
            <span className="ml-2 text-text-primary font-semibold">
              ${stats.high.toFixed(2)}
            </span>
          </div>
          <div>
            <span className="text-text-muted">24h Low:</span>
            <span className="ml-2 text-text-primary font-semibold">
              ${stats.low.toFixed(2)}
            </span>
          </div>
          <div>
            <span className="text-text-muted">Volume:</span>
            <span className="ml-2 text-text-primary font-semibold">
              {stats.volume.toFixed(2)}
            </span>
          </div>
          <div>
            <span className="text-text-muted">Change:</span>
            <span className={`ml-2 font-semibold ${
              stats.change > 0 ? 'text-accent-green' : 'text-accent-red'
            }`}>
              {stats.change > 0 ? '+' : ''}{stats.change.toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#00ff88" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#00ff88" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" opacity={0.3} />
            <XAxis 
              dataKey="time" 
              stroke="#6b7280"
              tick={{ fill: '#9ca3af', fontSize: 12 }}
              tickFormatter={(time) => {
                const date = new Date(time);
                return date.toLocaleTimeString('en-US', { 
                  hour: '2-digit', 
                  minute: '2-digit',
                  hour12: false 
                });
              }}
            />
            <YAxis 
              stroke="#6b7280"
              tick={{ fill: '#9ca3af', fontSize: 12 }}
              domain={['auto', 'auto']}
              tickFormatter={(value) => `$${value.toFixed(0)}`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke="#00ff88" 
              strokeWidth={2}
              dot={false}
              fill="url(#colorPrice)"
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-[300px] flex items-center justify-center text-text-muted">
          <div className="text-center">
            <p>No trade data available</p>
            <p className="text-sm mt-2">Chart will appear once trades are executed</p>
          </div>
        </div>
      )}
    </div>
  );
}