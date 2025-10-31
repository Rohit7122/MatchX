import { useState } from 'react';
import { ArrowUpRight, ArrowDownRight, Check, X } from 'lucide-react';

interface OrderFormProps {
  symbol: string;
  lastPrice: string;
}

export function OrderForm({ symbol, lastPrice }: OrderFormProps) {
  const [side, setSide] = useState<'buy' | 'sell'>('buy');
  const [orderType, setOrderType] = useState<'market' | 'limit' | 'ioc' | 'fok'>('limit');
  const [price, setPrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setMessage(null);

    try {
      const orderData = {
        symbol,
        order_type: orderType,
        side,
        quantity: parseFloat(quantity),
        ...(orderType !== 'market' && { price: parseFloat(price) })
      };

      const response = await fetch('http://localhost:8000/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });

      const result = await response.json();

      if (result.success) {
        setMessage({ 
          type: 'success', 
          text: `Order ${result.order.status}: ${result.trades?.length || 0} trades executed` 
        });
        // Reset form on successful market order or filled limit order
        if (orderType === 'market' || result.order.status === 'filled') {
          setQuantity('');
          if (orderType === 'limit') setPrice('');
        }
      } else {
        setMessage({ type: 'error', text: result.message || 'Order failed' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to submit order' });
      console.error('Order submission error:', error);
    } finally {
      setIsSubmitting(false);
      setTimeout(() => setMessage(null), 5000);
    }
  };

  const handlePercentage = (percent: number) => {
    // Simple percentage calculation - in production, would use actual balance
    const value = (parseFloat(lastPrice || '0') * percent).toString();
    setQuantity((parseFloat(value) / parseFloat(lastPrice || '1')).toFixed(6));
  };

  return (
    <div className="bg-dark-surface rounded-lg p-6">
      <h2 className="text-lg font-semibold mb-4">Place Order</h2>

      {/* Side Selector */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <button
          onClick={() => setSide('buy')}
          className={`py-3 rounded-lg font-semibold transition-all ${
            side === 'buy'
              ? 'bg-accent-green text-dark-bg'
              : 'bg-dark-elevated text-text-secondary hover:bg-dark-border'
          }`}
        >
          <ArrowUpRight className="inline mr-2" size={18} />
          Buy
        </button>
        <button
          onClick={() => setSide('sell')}
          className={`py-3 rounded-lg font-semibold transition-all ${
            side === 'sell'
              ? 'bg-accent-red text-white'
              : 'bg-dark-elevated text-text-secondary hover:bg-dark-border'
          }`}
        >
          <ArrowDownRight className="inline mr-2" size={18} />
          Sell
        </button>
      </div>

      {/* Order Type Selector */}
      <div className="grid grid-cols-4 gap-2 mb-4">
        {(['market', 'limit', 'ioc', 'fok'] as const).map((type) => (
          <button
            key={type}
            onClick={() => setOrderType(type)}
            className={`py-2 rounded-lg text-sm font-medium transition-all ${
              orderType === type
                ? 'bg-accent-blue text-white'
                : 'bg-dark-elevated text-text-secondary hover:bg-dark-border'
            }`}
          >
            {type.toUpperCase()}
          </button>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Price Input (not for market orders) */}
        {orderType !== 'market' && (
          <div>
            <label className="block text-sm text-text-secondary mb-2">
              Price (USDT)
            </label>
            <div className="relative">
              <input
                type="number"
                step="0.01"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder={lastPrice}
                className="w-full bg-dark-elevated border border-dark-border rounded-lg px-4 py-3 text-text-primary focus:outline-none focus:border-accent-blue transition-colors"
                required
              />
              <button
                type="button"
                onClick={() => setPrice(lastPrice)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-accent-blue hover:text-accent-green transition-colors"
              >
                Last Price
              </button>
            </div>
          </div>
        )}

        {/* Quantity Input */}
        <div>
          <label className="block text-sm text-text-secondary mb-2">
            Quantity ({symbol.split('-')[0]})
          </label>
          <input
            type="number"
            step="0.000001"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="0.00"
            className="w-full bg-dark-elevated border border-dark-border rounded-lg px-4 py-3 text-text-primary focus:outline-none focus:border-accent-blue transition-colors"
            required
          />
        </div>

        {/* Quick Amount Buttons */}
        <div className="grid grid-cols-4 gap-2">
          {[25, 50, 75, 100].map((percent) => (
            <button
              key={percent}
              type="button"
              onClick={() => handlePercentage(percent)}
              className="py-2 bg-dark-elevated hover:bg-dark-border rounded-lg text-xs text-text-secondary transition-colors"
            >
              {percent}%
            </button>
          ))}
        </div>

        {/* Order Summary */}
        {quantity && (orderType === 'market' || price) && (
          <div className="bg-dark-elevated rounded-lg p-4 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-text-muted">Order Type</span>
              <span className="text-text-primary font-medium">{orderType.toUpperCase()}</span>
            </div>
            {orderType !== 'market' && (
              <div className="flex justify-between text-sm">
                <span className="text-text-muted">Price</span>
                <span className="text-text-primary font-mono">${parseFloat(price).toLocaleString()}</span>
              </div>
            )}
            <div className="flex justify-between text-sm">
              <span className="text-text-muted">Quantity</span>
              <span className="text-text-primary font-mono">{parseFloat(quantity).toFixed(6)}</span>
            </div>
            <div className="flex justify-between text-sm pt-2 border-t border-dark-border">
              <span className="text-text-muted">Total (Est.)</span>
              <span className="text-text-primary font-semibold font-mono">
                ${(parseFloat(quantity) * parseFloat(price || lastPrice || '0')).toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}
              </span>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting || !quantity || (orderType !== 'market' && !price)}
          className={`w-full py-4 rounded-lg font-semibold text-lg transition-all ${
            side === 'buy'
              ? 'bg-accent-green hover:bg-accent-green/90 text-dark-bg'
              : 'bg-accent-red hover:bg-accent-red/90 text-white'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isSubmitting ? 'Submitting...' : `${side === 'buy' ? 'Buy' : 'Sell'} ${symbol.split('-')[0]}`}
        </button>
      </form>

      {/* Message Display */}
      {message && (
        <div className={`mt-4 p-4 rounded-lg flex items-center space-x-2 ${
          message.type === 'success' 
            ? 'bg-accent-green/10 border border-accent-green/30' 
            : 'bg-accent-red/10 border border-accent-red/30'
        }`}>
          {message.type === 'success' ? (
            <Check size={20} className="text-accent-green" />
          ) : (
            <X size={20} className="text-accent-red" />
          )}
          <span className={message.type === 'success' ? 'text-accent-green' : 'text-accent-red'}>
            {message.text}
          </span>
        </div>
      )}
    </div>
  );
}