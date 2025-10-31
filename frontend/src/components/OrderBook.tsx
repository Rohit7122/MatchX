import { useEffect, useState } from 'react';

interface OrderBookProps {
  bids: [string, string][];
  asks: [string, string][];
  symbol: string;
}

export function OrderBook({ bids, asks, symbol }: OrderBookProps) {
  const [spread, setSpread] = useState<number>(0);
  const [spreadPercent, setSpreadPercent] = useState<number>(0);

  useEffect(() => {
    if (bids.length > 0 && asks.length > 0) {
      const bestBid = parseFloat(bids[0][0]);
      const bestAsk = parseFloat(asks[0][0]);
      const spreadValue = bestAsk - bestBid;
      setSpread(spreadValue);
      setSpreadPercent((spreadValue / bestAsk) * 100);
    }
  }, [bids, asks]);

  const maxBidQty = Math.max(...bids.map(b => parseFloat(b[1])), 1);
  const maxAskQty = Math.max(...asks.map(a => parseFloat(a[1])), 1);

  return (
    <div className="bg-dark-surface rounded-lg p-4 h-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold">Order Book</h2>
        <span className="text-xs text-text-muted">{symbol}</span>
      </div>

      {/* Header */}
      <div className="grid grid-cols-3 text-xs text-text-muted mb-2 px-2">
        <div>Price</div>
        <div className="text-right">Amount</div>
        <div className="text-right">Total</div>
      </div>

      {/* Asks (Sell Orders) - Lowest at bottom */}
      <div className="space-y-0.5 mb-3">
        {asks.slice(0, 10).reverse().map((ask, idx) => {
          const [price, quantity] = ask;
          const qty = parseFloat(quantity);
          const total = parseFloat(price) * qty;
          const widthPercent = (qty / maxAskQty) * 100;

          return (
            <div key={`ask-${idx}`} className="relative group cursor-pointer">
              <div 
                className="absolute right-0 top-0 h-full bg-accent-red opacity-10 transition-all group-hover:opacity-20"
                style={{ width: `${widthPercent}%` }}
              />
              <div className="relative grid grid-cols-3 text-sm py-1 px-2 hover:bg-dark-elevated rounded transition-colors">
                <div className="text-accent-red font-mono">
                  {parseFloat(price).toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </div>
                <div className="text-right text-text-secondary font-mono text-xs">
                  {parseFloat(quantity).toFixed(4)}
                </div>
                <div className="text-right text-text-muted font-mono text-xs">
                  {total.toFixed(2)}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Spread */}
      <div className="bg-dark-elevated rounded-lg py-3 px-4 mb-3">
        <div className="flex items-center justify-between">
          <span className="text-xs text-text-muted">Spread</span>
          <div className="text-right">
            <div className="text-sm font-semibold text-text-primary">
              ${spread.toFixed(2)}
            </div>
            <div className="text-xs text-text-muted">
              {spreadPercent.toFixed(3)}%
            </div>
          </div>
        </div>
      </div>

      {/* Bids (Buy Orders) - Highest at top */}
      <div className="space-y-0.5">
        {bids.slice(0, 10).map((bid, idx) => {
          const [price, quantity] = bid;
          const qty = parseFloat(quantity);
          const total = parseFloat(price) * qty;
          const widthPercent = (qty / maxBidQty) * 100;

          return (
            <div key={`bid-${idx}`} className="relative group cursor-pointer">
              <div 
                className="absolute right-0 top-0 h-full bg-accent-green opacity-10 transition-all group-hover:opacity-20"
                style={{ width: `${widthPercent}%` }}
              />
              <div className="relative grid grid-cols-3 text-sm py-1 px-2 hover:bg-dark-elevated rounded transition-colors">
                <div className="text-accent-green font-mono">
                  {parseFloat(price).toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </div>
                <div className="text-right text-text-secondary font-mono text-xs">
                  {parseFloat(quantity).toFixed(4)}
                </div>
                <div className="text-right text-text-muted font-mono text-xs">
                  {total.toFixed(2)}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {bids.length === 0 && asks.length === 0 && (
        <div className="text-center py-12 text-text-muted">
          <p>No orders in book</p>
          <p className="text-xs mt-2">Submit an order to get started</p>
        </div>
      )}
    </div>
  );
}