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
        throw new Error(data.detail?.message || 'Failed to generate drafts');
      }

      const data = await response.json();
      setDrafts(data.drafts);
      setViolations(data.violations || []);
      setPriceData(data.price_data);

    } catch (err: any) {
      setError(err.message);
    } finally {
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
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          <p className="font-bold">Error generating drafts:</p>
          <p>{error}</p>
          <div className="mt-2">
            <Link href="/settings" className="text-blue-600 underline">Check Settings</Link>
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

            <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
              <span>Verified: {draft.pounds} lbs @ ${draft.price_per_lb}/lb</span>
              <span>Total: ${(draft.pounds * draft.price_per_lb).toLocaleString()}</span>
            </div>

            {!sentMessages.includes(draft.message_id) && (
              <button
                onClick={() => handleSend(draft.message_id)}
                disabled={sending === draft.message_id}
                className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
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
