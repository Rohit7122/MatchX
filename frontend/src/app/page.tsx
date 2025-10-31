'use client';

import { useState, useEffect } from 'react';
import { OrderBook } from '@/components/OrderBook';
import { TradeHistory } from '@/components/TradeHistory';
import { OrderForm } from '@/components/OrderForm';
import { PriceChart } from '@/components/PriceChart';
import { Header } from '@/components/Header';
import { useWebSocket } from '@/hooks/useWebSocket';

interface Trade {
  trade_id: string;
  symbol: string;
  price: string;
  quantity: string;
  timestamp: string;
  aggressor_side: string;
}

interface OrderBookData {
  bids: [string, string][];
  asks: [string, string][];
  timestamp: string;
  symbol: string;
}

export default function TradingPage() {
  const [selectedSymbol, setSelectedSymbol] = useState('BTC-USDT');
  const [trades, setTrades] = useState<Trade[]>([]);
  const [orderBook, setOrderBook] = useState<OrderBookData>({
    bids: [],
    asks: [],
    timestamp: '',
    symbol: selectedSymbol
  });
  const [lastPrice, setLastPrice] = useState<string>('0');

  const { isConnected, lastMessage, subscribe } = useWebSocket('ws://localhost:8765');

  useEffect(() => {
    if (isConnected) {
      subscribe('trades');
      subscribe('orderbook');
    }
  }, [isConnected, subscribe]);

  useEffect(() => {
    if (!lastMessage) return;

    if (lastMessage.type === 'trade' && lastMessage.data) {
      const trade = lastMessage.data as Trade;
      if (trade.symbol === selectedSymbol) {
        setTrades(prev => [trade, ...prev.slice(0, 49)]);
        setLastPrice(trade.price);
      }
    } else if (lastMessage.type === 'orderbook' && lastMessage.data) {
      const bookData = lastMessage.data as OrderBookData;
      if (bookData.symbol === selectedSymbol) {
        setOrderBook(bookData);
      }
    }
  }, [lastMessage, selectedSymbol]);

  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        // Fetch order book
        const bookRes = await fetch(`http://localhost:8000/api/orderbook/${selectedSymbol}`);
        const bookData = await bookRes.json();
        setOrderBook(bookData);

        // Fetch recent trades
        const tradesRes = await fetch(`http://localhost:8000/api/trades?symbol=${selectedSymbol}&limit=50`);
        const tradesData = await tradesRes.json();
        setTrades(tradesData.trades || []);

        // Set initial price
        if (tradesData.trades && tradesData.trades.length > 0) {
          setLastPrice(tradesData.trades[0].price);
        }
      } catch (error) {
        console.error('Failed to fetch initial data:', error);
      }
    };

    fetchInitialData();
    const interval = setInterval(fetchInitialData, 5000);
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  return (
    <div className="min-h-screen bg-dark-bg text-text-primary">
      <Header 
        isConnected={isConnected} 
        selectedSymbol={selectedSymbol}
        onSymbolChange={setSelectedSymbol}
        lastPrice={lastPrice}
      />
      
      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Left Column - Order Book */}
          <div className="lg:col-span-3">
            <OrderBook 
              bids={orderBook.bids} 
              asks={orderBook.asks}
              symbol={selectedSymbol}
            />
          </div>

          {/* Center Column - Chart and Order Form */}
          <div className="lg:col-span-6 space-y-4">
            <PriceChart 
              trades={trades}
              symbol={selectedSymbol}
            />
            <OrderForm 
              symbol={selectedSymbol}
              lastPrice={lastPrice}
            />
          </div>

          {/* Right Column - Trade History */}
          <div className="lg:col-span-3">
            <TradeHistory trades={trades} />
          </div>
        </div>
      </div>
    </div>
  );
}