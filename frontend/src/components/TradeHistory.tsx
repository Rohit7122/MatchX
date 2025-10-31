import { Clock } from 'lucide-react';

interface Trade {
  trade_id: string;
  symbol: string;
  price: string;
  quantity: string;
  timestamp: string;
  aggressor_side: string;
}

interface TradeHistoryProps {
  trades: Trade[];
}

export function TradeHistory({ trades }: TradeHistoryProps) {
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit',
      hour12: false 
    });
  };

  return (
    <div className="bg-dark-surface rounded-lg p-4 h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Recent Trades</h2>
        <Clock size={16} className="text-text-muted" />
      </div>

      {/* Header */}
      <div className="grid grid-cols-3 text-xs text-text-muted mb-2 px-2">
        <div>Price</div>
        <div className="text-right">Amount</div>
        <div className="text-right">Time</div>
      </div>

      {/* Trades List */}
      <div className="space-y-0.5 max-h-[600px] overflow-y-auto custom-scrollbar">
        {trades.map((trade, idx) => {
          const isBuy = trade.aggressor_side === 'buy';
          
          return (
            <div
              key={trade.trade_id}
              className={`grid grid-cols-3 text-sm py-2 px-2 rounded transition-all hover:bg-dark-elevated ${
                idx === 0 ? 'animate-pulse-slow' : ''
              }`}
            >
              <div className={`font-mono font-semibold ${
                isBuy ? 'text-accent-green' : 'text-accent-red'
              }`}>
                {parseFloat(trade.price).toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </div>
              <div className="text-right text-text-secondary font-mono text-xs">
                {parseFloat(trade.quantity).toFixed(4)}
              </div>
              <div className="text-right text-text-muted text-xs">
                {formatTime(trade.timestamp)}
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {trades.length === 0 && (
        <div className="text-center py-12 text-text-muted">
          <p>No trades yet</p>
          <p className="text-xs mt-2">Trades will appear here as they execute</p>
        </div>
      )}
    </div>
  );
}