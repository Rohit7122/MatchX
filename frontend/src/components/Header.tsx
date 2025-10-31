import { Activity, TrendingUp, TrendingDown } from 'lucide-react';
import { useState, useEffect } from 'react';

interface HeaderProps {
  isConnected: boolean;
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
  lastPrice: string;
}

export function Header({ isConnected, selectedSymbol, onSymbolChange, lastPrice }: HeaderProps) {
  const [priceChange, setPriceChange] = useState(0);
  const [prevPrice, setPrevPrice] = useState<string>(lastPrice);

  useEffect(() => {
    if (prevPrice !== '0' && lastPrice !== '0') {
      const change = ((parseFloat(lastPrice) - parseFloat(prevPrice)) / parseFloat(prevPrice)) * 100;
      setPriceChange(change);
    }
    setPrevPrice(lastPrice);
  }, [lastPrice]);

  const symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'XRP-USDT'];

  return (
    <header className="bg-dark-surface border-b border-dark-border sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-accent-green to-accent-blue rounded-lg flex items-center justify-center">
                <span className="text-xl font-bold">ME</span>
              </div>
              <div>
                <h1 className="text-xl font-bold">Matching Engine</h1>
                <p className="text-xs text-text-muted">High-Performance Trading</p>
              </div>
            </div>
          </div>

          {/* Symbol Selector */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-2 bg-dark-elevated px-4 py-2 rounded-lg">
              {symbols.map(symbol => (
                <button
                  key={symbol}
                  onClick={() => onSymbolChange(symbol)}
                  className={`px-3 py-1.5 rounded transition-all ${
                    selectedSymbol === symbol
                      ? 'bg-accent-green text-dark-bg font-semibold'
                      : 'text-text-secondary hover:text-text-primary'
                  }`}
                >
                  {symbol.split('-')[0]}
                </button>
              ))}
            </div>

            {/* Price Display */}
            <div className="bg-dark-elevated px-6 py-2 rounded-lg">
              <div className="text-xs text-text-muted mb-1">{selectedSymbol}</div>
              <div className="flex items-center space-x-3">
                <span className={`text-2xl font-bold ${
                  priceChange > 0 ? 'text-accent-green' : priceChange < 0 ? 'text-accent-red' : 'text-text-primary'
                }`}>
                  ${parseFloat(lastPrice).toLocaleString(undefined, {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </span>
                {priceChange !== 0 && (
                  <div className={`flex items-center text-sm ${
                    priceChange > 0 ? 'text-accent-green' : 'text-accent-red'
                  }`}>
                    {priceChange > 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                    <span className="ml-1">{Math.abs(priceChange).toFixed(2)}%</span>
                  </div>
                )}
              </div>
            </div>

            {/* Connection Status */}
            <div className="flex items-center space-x-2">
              <Activity 
                size={20} 
                className={isConnected ? 'text-accent-green animate-pulse' : 'text-text-muted'} 
              />
              <span className="text-sm text-text-secondary">
                {isConnected ? 'Live' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}