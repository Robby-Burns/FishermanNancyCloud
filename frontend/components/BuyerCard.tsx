'use client';

interface Buyer {
  id: number;
  name: string;
  phone: string;
  carrier: string;
  preferred_fish: string;
}

interface BuyerCardProps {
  buyer: Buyer;
}

export default function BuyerCard({ buyer }: BuyerCardProps) {
  return (
    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex justify-between items-center">
      <div>
        <h3 className="font-bold text-gray-900">{buyer.name}</h3>
        <p className="text-sm text-gray-500">{buyer.phone} • {buyer.carrier}</p>
        {buyer.preferred_fish && (
          <div className="mt-1 flex gap-1">
            {buyer.preferred_fish.split(',').map((fish, i) => (
              <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full">
                {fish.trim()}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
