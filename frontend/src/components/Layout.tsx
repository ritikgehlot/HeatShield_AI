import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout() {
  return (
    <div className="min-h-screen bg-[#0a0f1c]">
      <Sidebar />
      <main className="ml-[240px] min-h-screen transition-all duration-300">
        <Outlet />
      </main>
    </div>
  );
}
