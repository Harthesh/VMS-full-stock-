import Header from "./Header";
import Sidebar from "./Sidebar";

export default function AppLayout({ children }) {
  return (
    <div className="mx-auto max-w-[1600px] px-4 py-4 lg:px-6">
      <div className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
        <Sidebar />
        <main className="min-w-0">
          <Header />
          {children}
        </main>
      </div>
    </div>
  );
}

