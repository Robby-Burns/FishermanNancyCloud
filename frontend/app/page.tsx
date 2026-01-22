'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Dashboard() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
    } else {
      setIsAuthenticated(true);
    }
  }, [router]);

  if (!isAuthenticated) return null;

  const menuItems = [
    {
      title: "Log Catch",
      description: "Record today's catch",
      href: "/log-catch",
      color: "bg-blue-600",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
      )
    },
    {
      title: "Contact Buyers",
      description: "Generate & send messages",
      href: "/contact-buyers",
      color: "bg-green-600",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z" />
        </svg>
      )
    },
    {
      title: "Catch History",
      description: "View past catches & sales",
      href: "/catch-history",
      color: "bg-indigo-600",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
        </svg>
      )
    },
    {
      title: "Buyer Management",
      description: "Manage contacts",
      href: "/buyer-management",
      color: "bg-purple-600",
      icon: (
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-8 h-8">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />
        </svg>
      )
    }
  ];

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <h1 className="text-2xl font-bold text-gray-900">Welcome, Captain</h1>
        <p className="text-gray-500 mt-1">What would you like to do today?</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="flex items-center p-6 bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
          >
            <div className={`${item.color} p-3 rounded-lg text-white mr-4`}>
              {item.icon}
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{item.title}</h2>
              <p className="text-sm text-gray-500">{item.description}</p>
            </div>
          </Link>
        ))}
      </div>

      <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
        <h3 className="font-semibold text-blue-900 mb-2">Current Prices (Westport)</h3>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-white p-2 rounded shadow-sm">
            <div className="text-xs text-gray-500">Crab</div>
            <div className="font-bold text-gray-900">$5.50</div>
          </div>
          <div className="bg-white p-2 rounded shadow-sm">
            <div className="text-xs text-gray-500">Salmon</div>
            <div className="font-bold text-gray-900">$4.20</div>
          </div>
          <div className="bg-white p-2 rounded shadow-sm">
            <div className="text-xs text-gray-500">Halibut</div>
            <div className="font-bold text-gray-900">$4.80</div>
          </div>
        </div>
      </div>
    </div>
  );
}
