'use client';

interface Message {
  id: number;
  message_text: string;
  sent_at: string;
  status: string;
  buyer_id?: number;
  buyer?: {
    name: string;
  };
}

interface ConversationThreadProps {
  messages: Message[];
}

export default function ConversationThread({ messages }: ConversationThreadProps) {
  if (messages.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-xl border border-gray-100">
        <p className="text-gray-500">No messages sent yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {messages.map((msg) => (
        <div key={msg.id} className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <div className="flex justify-between items-start mb-2">
            <span className="font-semibold text-gray-900">
              To: {msg.buyer?.name || `Buyer #${msg.buyer_id}`}
            </span>
            <span className="text-xs text-gray-500">
              {msg.sent_at ? new Date(msg.sent_at).toLocaleString() : 'Draft'}
            </span>
          </div>
          <p className="text-gray-700 text-sm bg-gray-50 p-3 rounded-lg">
            {msg.message_text}
          </p>
          <div className="mt-2 flex justify-end">
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${
              msg.status === 'sent' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {msg.status.toUpperCase()}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
}
