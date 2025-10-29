export default function Notes() {
  const items = [
    { at: new Date().toLocaleString(), who: "System", text: "Guest notes API not found. Showing placeholder data." },
    { at: new Date(Date.now() - 86400000).toLocaleString(), who: "Front Desk", text: "Room 305 requests late checkout (11:30)." },
  ];
  return (
    <div className="card">
      <h3>Guest Notes & Incidents</h3>
      <table className="table">
        <thead><tr><th>When</th><th>Author</th><th>Note</th></tr></thead>
        <tbody>
          {items.map((n,i)=>(
            <tr key={i}><td>{n.at}</td><td>{n.who}</td><td>{n.text}</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
