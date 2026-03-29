import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import HistoryPage from "./pages/HistoryPage";
import MonitoringPage from "./pages/MonitoringPage";
import PredictPage from "./pages/PredictPage";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<PredictPage />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/monitoring" element={<MonitoringPage />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
