interface ListItem {
  label: string;
  value: string | number;
}

interface ListCardProps {
  title: string;
  items: ListItem[];
  emptyMessage?: string;
}

export default function ListCard({ title, items, emptyMessage = "No data available" }: ListCardProps) {
  return (
    <div className="flex h-full flex-col rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-sm font-semibold text-slate-600">{title}</h3>
      <div className="mt-4 grow space-y-3">
        {items.length === 0 ? (
          <p className="text-sm text-slate-500">{emptyMessage}</p>
        ) : (
          items.map((item) => (
            <div key={item.label} className="flex items-center justify-between text-sm text-slate-700">
              <span>{item.label}</span>
              <span className="font-semibold text-slate-900">{item.value}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
