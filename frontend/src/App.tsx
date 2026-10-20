import { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { VideoAssistantWorkspace } from './components/VideoAssistantWorkspace';
import { ResearchAgentWorkspace } from './components/ResearchAgentWorkspace';
import { ChatAssistantWorkspace } from './components/ChatAssistantWorkspace';
import { DocumentAssistantWorkspace } from './components/DocumentAssistantWorkspace';
import { CommandPalette } from './components/CommandPalette';
import type { SystemHealth } from './types';

export function App() {
  const [currentPage, setCurrentPage] = useState<string>('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [isCommandOpen, setIsCommandOpen] = useState<boolean>(false);
  const [health, setHealth] = useState<SystemHealth | null>(null);

  // Fetch telemetry from FastAPI backend
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          const data = await res.json();
          setHealth(data);
        }
      } catch (err) {
        console.warn('Backend telemetry not yet connected:', err);
      }
    };
    fetchHealth();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#09090b] text-[#f8fafc]">
      {/* Sidebar navigation */}
      <Sidebar
        currentPage={currentPage}
        onNavigate={(pageId) => setCurrentPage(pageId)}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />

      {/* Main View Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Header */}
        <Header
          currentPage={currentPage}
          onOpenCommand={() => setIsCommandOpen(true)}
          health={health}
        />

        {/* Scrollable Workspace View */}
        <main className="flex-1 overflow-y-auto bg-grid-pattern">
          {currentPage === 'video_assistant' ? (
            <VideoAssistantWorkspace onBackToHub={() => setCurrentPage('dashboard')} />
          ) : currentPage === 'research_agent' ? (
            <ResearchAgentWorkspace onBackToHub={() => setCurrentPage('dashboard')} />
          ) : currentPage === 'chat_assistant' ? (
            <ChatAssistantWorkspace onBackToHub={() => setCurrentPage('dashboard')} />
          ) : currentPage === 'document_assistant' ? (
            <DocumentAssistantWorkspace onBackToHub={() => setCurrentPage('dashboard')} />
          ) : (
            <Dashboard onSelectModule={(moduleId) => setCurrentPage(moduleId)} />
          )}
        </main>
      </div>

      {/* Command Palette (⌘K) */}
      <CommandPalette
        isOpen={isCommandOpen}
        onClose={() => setIsCommandOpen(false)}
        onSelectModule={(moduleId) => setCurrentPage(moduleId)}
      />
    </div>
  );
}

export default App;
