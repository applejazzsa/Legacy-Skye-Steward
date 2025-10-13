export interface Handover {
  id: number;
  outlet: string;
  date: string;
  shift: string;
  period: string | null;
  bookings: number;
  walk_ins: number;
  covers: number;
  food_revenue: number;
  beverage_revenue: number;
  top_sales: string[];
}

interface HandoversTableProps {
  handovers: Handover[];
}

export default function HandoversTable({ handovers }: HandoversTableProps) {
  if (!handovers || handovers.length === 0) {
    return (
      <div className="rounded-lg border border-slate-200 bg-white p-6 text-center text-sm text-slate-500 shadow-sm">
        No recent handovers. Create one to get started.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-100 text-left">
          <tr>
            <th className="px-4 py-2 font-semibold">Outlet</th>
            <th className="px-4 py-2 font-semibold">Date</th>
            <th className="px-4 py-2 font-semibold">Shift</th>
            <th className="px-4 py-2 font-semibold">Covers</th>
            <th className="px-4 py-2 font-semibold">Revenue</th>
            <th className="px-4 py-2 font-semibold">Top Sales</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {handovers.slice(0, 10).map((handover) => {
            const date = new Date(handover.date);
            const revenue = handover.food_revenue + handover.beverage_revenue;
            return (
              <tr key={handover.id} className="hover:bg-slate-50">
                <td className="px-4 py-2">{handover.outlet}</td>
                <td className="px-4 py-2">
                  {date.toLocaleDateString()} {" "}
                  <span className="text-xs text-slate-500">
                    {handover.period ?? handover.shift}
                  </span>
                </td>
                <td className="px-4 py-2">{handover.shift}</td>
                <td className="px-4 py-2">{handover.covers}</td>
                <td className="px-4 py-2">
                  {revenue.toLocaleString(undefined, {
                    style: "currency",
                    currency: "USD",
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </td>
                <td className="px-4 py-2">
                  {handover.top_sales?.length ? handover.top_sales.join(", ") : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
