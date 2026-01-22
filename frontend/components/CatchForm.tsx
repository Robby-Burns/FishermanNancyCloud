'use client';

import { useState } from 'react';

interface CatchFormProps {
  onSubmit: (fishType: string, pounds: number) => Promise<void>;
  loading: boolean;
}

export default function CatchForm({ onSubmit, loading }: CatchFormProps) {
  const [fishType, setFishType] = useState('Halibut');
  const [pounds, setPounds] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(fishType, parseFloat(pounds));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Fish Type</label>
        <div className="grid grid-cols-2 gap-3">
          {['Halibut', 'Salmon', 'Crab', 'Other'].map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => setFishType(type)}
              className={`py-3 px-4 rounded-lg border text-sm font-medium transition-colors ${
                fishType === type
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label htmlFor="pounds" className="block text-sm font-medium text-gray-700 mb-2">
          Weight (lbs)
        </label>
        <div className="relative rounded-md shadow-sm">
          <input
            type="number"
            name="pounds"
            id="pounds"
            className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-4 pr-12 py-4 sm:text-lg border-gray-300 rounded-lg"
            placeholder="0"
            value={pounds}
            onChange={(e) => setPounds(e.target.value)}
            required
            min="1"
            step="0.1"
          />
          <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none">
            <span className="text-gray-500 sm:text-sm">lbs</span>
          </div>
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !pounds}
        className="w-full flex justify-center py-4 px-4 border border-transparent rounded-xl shadow-sm text-lg font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {loading ? 'Saving...' : 'Save & Contact Buyers'}
      </button>
    </form>
  );
}
