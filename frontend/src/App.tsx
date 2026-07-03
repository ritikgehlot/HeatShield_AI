import { Route, Routes } from "react-router-dom";
import { AppLayout } from "@/components/AppLayout";
import { LandingPage } from "@/pages/LandingPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { WardDetailPage } from "@/pages/WardDetailPage";
import { SimulatorPage } from "@/pages/SimulatorPage";
import { DataSourcesPage } from "@/pages/DataSourcesPage";
import { AboutPage } from "@/pages/AboutPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route element={<AppLayout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/wards/:wardId" element={<WardDetailPage />} />
        <Route path="/simulator" element={<SimulatorPage />} />
        <Route path="/simulator/:wardId" element={<SimulatorPage />} />
        <Route path="/data-sources" element={<DataSourcesPage />} />
        <Route path="/about" element={<AboutPage />} />
      </Route>
    </Routes>
  );
}
