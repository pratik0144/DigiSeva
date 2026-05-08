import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { SessionProvider, useSession } from './context/SessionContext';
import { Layout } from './components/layout/Layout';
import { Home } from './pages/Home';
import { Transactions } from './pages/Transactions';
import { Schemes } from './pages/Schemes';
import { Education } from './pages/Education';
import { VoiceInteraction } from './pages/VoiceInteraction';
import { Login } from './pages/Login';

const AppContent = () => {
  const { profile, isInitialized } = useSession();

  if (!isInitialized && !profile) {
    // SessionContext auto-logs in JD-1001 on mount.
    // While it's initializing, we can return null or a loader.
    // But if they logged out, isInitialized is false and profile is null, so show Login.
    return <Login />;
  }

  if (!profile) {
    return <Login />;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="transactions" element={<Transactions />} />
          <Route path="schemes" element={<Schemes />} />
          <Route path="education" element={<Education />} />
        </Route>
        {/* Voice is outside layout to be fullscreen overlay on mobile */}
        <Route path="/voice" element={<VoiceInteraction />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

function App() {
  return (
    <SessionProvider>
      <AppContent />
    </SessionProvider>
  );
}

export default App;
