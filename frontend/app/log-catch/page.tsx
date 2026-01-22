'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LogCatch() {
  const router = useRouter();
  const [fishType, setFishType] = useState('Halibut');
  const [pounds, setPounds] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/catches`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          fish_type: fishType,
          pounds: parseFloat(pounds)
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail?.message || 'Failed to log catch');
      }

      // Success - redirect to contact buyers
      const catchData = await response.json();
      router.push(`/contact-buyers?catch_id=${catchData.id}`);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/" className="text-gray-500 hover:text-gray-900">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Log Catch</h1>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
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

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading || !pounds}
            className="w-full flex justify-center py-4 px-4 border border-transparent rounded-xl shadow-sm text-lg font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Saving...' : 'Save & Contact Buyers'}
          </button>
        </form>
      </div>
    </div>
  );
}
