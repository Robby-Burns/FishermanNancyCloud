'use client';

import { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';

function ContactBuyersContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const catchId = searchParams.get('catch_id');

  const [loading, setLoading] = useState(true);
  const [drafts, setDrafts] = useState<any[]>([]);
  const [violations, setViolations] = useState<any[]>([]);
  const [priceData, setPriceData] = useState<any>(null);
  const [error, setError] = useState('');
  const [missingPrice, setMissingPrice] = useState(false);
  const [manualPrice, setManualPrice] = useState('');
  const [sending, setSending] = useState<number | null>(null);
  const [sentMessages, setSentMessages] = useState<number[]>([]);

  useEffect(() => {
    if (!catchId) {
      router.push('/log-catch');
      return;
    }
    fetchDrafts();
  }, [catchId]);

  const fetchDrafts = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/contact-buyers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ catch_id: parseInt(catchId!) }),
      });

      if (!response.ok) {
        const data = await response.json();

        // Handle missing price specifically
        if (data.detail && data.detail.missing_price) {
            setMissingPrice(true);
            setLoading(false);
            return;
        }

        // Handle other violations
        if (data.detail && data.detail.violations) {
            setViolations(data.detail.violations);
            throw new Error(data.detail.message || 'Safety check failed');
        }
        throw new Error(data.detail?.message || 'Failed to generate drafts');
      }

      const data = await response.json();
      setDrafts(data.drafts);
      setViolations(data.violations || []);
      setPriceData(data.price_data);
      setMissingPrice(false);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleManualPriceSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
        const token = localStorage.getItem('token');
        // Actually, the backend endpoint expects query params for manual price
        const fishType = 'Halibut'; // Default for now
        const url = new URL(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/prices/manual`);
        url.searchParams.append('fish_type', fishType);
        url.searchParams.append('price_per_lb', manualPrice);

        await fetch(url.toString(), {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        // 2. Retry fetching drafts
        setMissingPrice(false);
        fetchDrafts();

    } catch (err: any) {
        setError(err.message);
        setLoading(false);
    }
  };

  const handleSend = async (messageId: number) => {
    setSending(messageId);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/messages/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message_id: messageId }),
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      setSentMessages(prev => [...prev, messageId]);

    } catch (err: any) {
      alert(err.message);
    } finally {
      setSending(null);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
        <p className="text-gray-500">AI is checking prices and writing drafts...</p>
      </div>
    );
  }

  if (missingPrice) {
      return (
        <div className="max-w-md mx-auto mt-10 bg-white p-8 rounded-xl shadow-lg border border-yellow-200">
            <div className="text-center mb-6">
                <div className="mx-auto h-12 w-12 bg-yellow-100 rounded-full flex items-center justify-center mb-4">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-yellow-600">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
                    </svg>
                </div>
                <h2 className="text-xl font-bold text-gray-900">Price Not Found</h2>
                <p className="text-gray-500 mt-2">The AI couldn't find today's price online. Please enter it manually to continue.</p>
            </div>

            <form onSubmit={handleManualPriceSubmit} className="space-y-4">
                <div>
                    <label htmlFor="price" className="block text-sm font-medium text-gray-700 mb-1">Price per Pound ($)</label>
                    <div className="relative rounded-md shadow-sm">
                        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                            <span className="text-gray-500 sm:text-sm">$</span>
                        </div>
                        <input
                            type="number"
                            step="0.01"
                            name="price"
                            id="price"
                            className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-7 pr-12 py-3 sm:text-lg border-gray-300 rounded-lg text-black"
                            placeholder="0.00"
                            value={manualPrice}
                            onChange={(e) => setManualPrice(e.target.value)}
                            required
                        />
                    </div>
                </div>
                <button
                    type="submit"
                    className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                    Set Price & Continue
                </button>
            </form>
        </div>
      );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Link href="/" className="text-gray-500 hover:text-gray-900">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
          </svg>
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Review Drafts</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 p-6 rounded-xl shadow-sm">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-medium text-red-800">Action Required</h3>
              <p className="mt-1 text-sm text-red-700">{error}</p>

              {violations.length > 0 && (
                <div className="mt-4 bg-white p-4 rounded-lg border border-red-100">
                  <h4 className="text-sm font-semibold text-red-800 mb-2">Why was this blocked?</h4>
                  <ul className="list-disc list-inside space-y-1">
                    {violations.map((v: any, i) => (
                      <li key={i} className="text-sm text-gray-700">
                        {typeof v === 'string' ? v : v.violation_description || v.coaching_delivered}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <div className="mt-4 flex space-x-3">
                <Link
                  href="/settings"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Check Settings
                </Link>
                <Link
                  href="/log-catch"
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Edit Catch
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {priceData && (
        <div className="bg-blue-50 p-4 rounded-xl border border-blue-100 flex justify-between items-center">
          <div>
            <div className="text-sm text-blue-800">Current Price ({priceData.cannery_name})</div>
            <div className="text-2xl font-bold text-blue-900">${priceData.price_per_lb}/lb</div>
            <div className="text-xs text-blue-600 mt-1">
              Updated: {new Date().toLocaleTimeString()}
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-800">Fish Type</div>
            <div className="font-semibold text-blue-900">{priceData.fish_type}</div>
          </div>
        </div>
      )}

      {drafts.length === 0 && !error && (
        <div className="text-center py-12 bg-white rounded-xl border border-gray-100">
          <p className="text-gray-500">No buyers found for this fish type.</p>
          <Link href="/buyer-management" className="text-blue-600 font-medium mt-2 inline-block">
            Add Buyers
          </Link>
        </div>
      )}

      <div className="space-y-4">
        {drafts.map((draft) => (
          <div key={draft.message_id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="font-bold text-gray-900">{draft.buyer_name}</h3>
                <p className="text-xs text-gray-500">Draft Message</p>
              </div>
              {sentMessages.includes(draft.message_id) ? (
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">
                  Sent
                </span>
              ) : (
                <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full font-medium">
                  Draft
                </span>
              )}
            </div>

            <div className="bg-gray-50 p-4 rounded-lg text-gray-800 mb-4 font-mono text-sm">
              {draft.message_text}
            </div>

            {/* Human-Centered Design: Trust Signals */}
            <div className="mt-4 border-t border-gray-100 pt-4">
                <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
                    <div className="flex items-center space-x-2">
                        <span className="h-2 w-2 rounded-full bg-green-500"></span>
                        <span className="font-medium text-gray-700">High Confidence</span>
                    </div>
                    <span>Source: {priceData?.cannery_name || 'Manual Entry'}</span>
                </div>

                <details className="group">
                    <summary className="text-xs text-blue-600 cursor-pointer hover:text-blue-800 list-none flex items-center">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-3 h-3 mr-1 group-open:rotate-90 transition-transform">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                        </svg>
                        How this was generated
                    </summary>
                    <div className="mt-2 text-xs text-gray-600 bg-gray-50 p-3 rounded border border-gray-100">
                        <p className="mb-1"><strong>Logic:</strong></p>
                        <ul className="list-disc list-inside space-y-1 pl-1">
                            <li>Verified catch: {draft.pounds} lbs</li>
                            <li>Verified price: ${draft.price_per_lb}/lb</li>
                            <li>Total value: ${(draft.pounds * draft.price_per_lb).toLocaleString()}</li>
                            <li>Buyer preference: Matches "{draft.fish_type}"</li>
                        </ul>
                    </div>
                </details>
            </div>

            {!sentMessages.includes(draft.message_id) && (
              <button
                onClick={() => handleSend(draft.message_id)}
                disabled={sending === draft.message_id}
                className="w-full mt-4 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {sending === draft.message_id ? 'Sending...' : 'Approve & Send'}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ContactBuyers() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ContactBuyersContent />
    </Suspense>
  );
}
