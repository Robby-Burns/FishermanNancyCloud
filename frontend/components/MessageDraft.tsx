'use client';

interface MessageDraftProps {
  draft: {
    message_id: number;
    buyer_name: string;
    message_text: string;
    pounds: number;
    price_per_lb: number;
  };
  onSend: (id: number) => void;
  sending: boolean;
  isSent: boolean;
}

export default function MessageDraft({ draft, onSend, sending, isSent }: MessageDraftProps) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="font-bold text-gray-900">{draft.buyer_name}</h3>
          <p className="text-xs text-gray-500">Draft Message</p>
        </div>
        {isSent ? (
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

      {!isSent && (
        <button
          onClick={() => onSend(draft.message_id)}
          disabled={sending}
          className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {sending ? 'Sending...' : 'Approve & Send'}
        </button>
      )}
    </div>
  );
}
