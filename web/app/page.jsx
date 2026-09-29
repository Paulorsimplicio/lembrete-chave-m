'use client';

import { useState, useEffect } from 'react';

export default function Home() {
  const [os, setOs] = useState('windows');
  const [versionData, setVersionData] = useState({
    version: 'v1.4.0',
    assets: {
      windows: { url: 'https://github.com/Paulorsimplicio/lembrete-chave-m/releases/latest/download/LembreteChaveM-Windows.zip', name: 'LembreteChaveM-Windows.zip' },
      macos: { url: 'https://github.com/Paulorsimplicio/lembrete-chave-m/releases/latest/download/LembreteChaveM-MacOS.zip', name: 'LembreteChaveM-MacOS.zip' },
      linux: { url: 'https://github.com/Paulorsimplicio/lembrete-chave-m/releases/latest/download/LembreteChaveM-Linux.zip', name: 'LembreteChaveM-Linux.zip' },
    }
  });
  const [activeTab, setActiveTab] = useState('windows');

  useEffect(() => {
    // Detect OS
    if (typeof window !== 'undefined') {
      const userAgent = window.navigator.userAgent.toLowerCase();
      if (userAgent.includes('mac')) {
        setOs('macos');
        setActiveTab('macos');
      } else if (userAgent.includes('linux')) {
        setOs('linux');
        setActiveTab('linux');
      } else {
        setOs('windows');
        setActiveTab('windows');
      }
    }

    // Fetch dynamic latest version & assets
    fetch('/api/version')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.assets) {
          setVersionData(data);
        }
      })
      .catch(() => {
        // Fallback already present
      });
  }, []);

  const getPrimaryDownload = () => {
    switch (os) {
      case 'macos':
        return {
          title: 'Baixar para macOS',
          format: 'Pacote .zip (LembreteChaveM.app + Manual de Uso)',
          url: versionData.assets?.macos?.url,
          icon: '🍏'
        };
      case 'linux':
        return {
          title: 'Baixar para Linux',
          format: 'Pacote .zip (Binário + Manual de Uso)',
          url: versionData.assets?.linux?.url,
          icon: '🐧'
        };
      case 'windows':
      default:
        return {
          title: 'Baixar para Windows',
          format: 'Pacote .zip (Executável .exe + Manual de Uso)',
          url: versionData.assets?.windows?.url,
          icon: '🪟'
        };
    }
  };

  const primary = getPrimaryDownload();

  return (
    <div>
      {/* Header / Navbar */}
      <header className="navbar">
        <div className="nav-container">
          <a href="#" className="brand-link">
            <img src="/icon.png" alt="Lembrete Chave M" className="brand-logo" />
            <span className="brand-title">Lembrete Chave M</span>
          </a>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <a 
              href="/Manual_de_Uso.html" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                color: '#38bdf8',
                fontSize: '0.85rem',
                fontWeight: '600',
                textDecoration: 'none',
                padding: '0.35rem 0.75rem',
                borderRadius: '8px',
                background: 'rgba(56, 189, 248, 0.1)',
                border: '1px solid rgba(56, 189, 248, 0.2)'
              }}
            >
              📖 Manual de Uso
            </a>
            <span className="badge-corp">FourSys Internal</span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="version-pill">
          <span className="status-dot"></span>
          <span>Versão {versionData.version} disponível</span>
        </div>

        <h1 className="hero-title">
          Nunca mais esqueça de preencher sua <span className="gradient-text">Chave M</span>
        </h1>

        <p className="hero-subtitle">
          Assistente leve e inteligente para desktop. Notifica nos horários ideais do expediente, respeita feriados e funciona em segundo plano sem atrapalhar seu fluxo.
        </p>

        {/* CTA Principal com Detecção de SO e Manual */}
        <div className="cta-wrapper">
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <a href={primary.url} className="btn-primary" id="btn-primary-download">
              <span style={{ fontSize: '1.4rem' }}>{primary.icon}</span>
              <span>{primary.title}</span>
            </a>
            <a 
              href="/Manual_de_Uso.html" 
              target="_blank" 
              rel="noopener noreferrer" 
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.6rem',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-subtle)',
                color: '#f8fafc',
                padding: '1.1rem 1.6rem',
                borderRadius: '14px',
                fontSize: '1rem',
                fontWeight: '600',
                textDecoration: 'none',
                transition: 'all 0.2s ease'
              }}
            >
              <span>📖</span>
              <span>Manual Online</span>
            </a>
          </div>
          <span className="os-detected-subtext">
            Detectado para o seu sistema: <strong>{primary.format}</strong>
          </span>
        </div>
      </section>

      {/* Todos os Sistemas Disponíveis */}
      <section className="downloads-container">
        <h2 className="downloads-title">Downloads para outros sistemas operacionais</h2>
        <div className="platforms-grid">
          
          {/* Card Windows */}
          <a href={versionData.assets?.windows?.url} className="glass-panel platform-card" id="download-windows">
            <div>
              <div className="platform-header">
                <div className="platform-icon-box">🪟</div>
                <div>
                  <div className="platform-name">Windows</div>
                  <div className="platform-format">Pacote .zip (.exe + Manual)</div>
                </div>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Compatível com Windows 10 e 11 (64 bits). Inclui executável e Manual de Uso.
              </p>
            </div>
            <div className="platform-action">
              <span>Baixar pacote com Manual</span>
              <span>↓</span>
            </div>
          </a>

          {/* Card macOS */}
          <a href={versionData.assets?.macos?.url} className="glass-panel platform-card" id="download-macos">
            <div>
              <div className="platform-header">
                <div className="platform-icon-box">🍏</div>
                <div>
                  <div className="platform-name">macOS</div>
                  <div className="platform-format">Pacote .zip (.app + Manual)</div>
                </div>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Compatível com Apple Silicon (M1/M2/M3/M4) e Intel. Inclui Manual de Uso.
              </p>
            </div>
            <div className="platform-action">
              <span>Baixar pacote com Manual</span>
              <span>↓</span>
            </div>
          </a>

          {/* Card Linux */}
          <a href={versionData.assets?.linux?.url} className="glass-panel platform-card" id="download-linux">
            <div>
              <div className="platform-header">
                <div className="platform-icon-box">🐧</div>
                <div>
                  <div className="platform-name">Linux</div>
                  <div className="platform-format">Pacote .zip (Binário + Manual)</div>
                </div>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Compatível com Ubuntu, Debian, Fedora e distribuições modernas.
              </p>
            </div>
            <div className="platform-action">
              <span>Baixar pacote com Manual</span>
              <span>↓</span>
            </div>
          </a>

        </div>
      </section>

      {/* Recursos e Vantagens */}
      <section className="features-section">
        <div className="section-badge">Produtividade Sem Estresse</div>
        <h2 className="section-heading">Projetado para o seu dia a dia na FourSys</h2>
        
        <div className="features-grid">
          <div className="glass-panel feature-card">
            <div className="feature-icon-wrapper">⏰</div>
            <h3 className="feature-title">Lembretes Pontuais</h3>
            <p className="feature-desc">
              Notificações suaves e sonoras nos horários configurados para você nunca deixar passar o registro.
            </p>
          </div>

          <div className="glass-panel feature-card">
            <div className="feature-icon-wrapper">🇧🇷</div>
            <h3 className="feature-title">Feriados Nacionais</h3>
            <p className="feature-desc">
              Sabe exatamente quando é feriado ou ponto facultativo e não envia avisos em dias não úteis.
            </p>
          </div>

          <div className="glass-panel feature-card">
            <div className="feature-icon-wrapper">🚀</div>
            <h3 className="feature-title">Bandeja do Sistema</h3>
            <p className="feature-desc">
              Fica discretamente recolhido ao lado do relógio do sistema, consumindo o mínimo de memória RAM.
            </p>
          </div>

          <div className="glass-panel feature-card">
            <div className="feature-icon-wrapper">🔒</div>
            <h3 className="feature-title">100% Offline e Seguro</h3>
            <p className="feature-desc">
              Sem coleta de dados confidenciais ou envio de credenciais. Todo o processamento é local.
            </p>
          </div>
        </div>
      </section>

      {/* Guia Rápido de Instalação */}
      <section className="guide-section">
        <div className="glass-panel guide-box">
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '1.5rem', textAlign: 'center' }}>
            Como Iniciar no seu Computador
          </h2>

          <div className="guide-tabs">
            <button 
              className={`guide-tab-btn ${activeTab === 'windows' ? 'active' : ''}`}
              onClick={() => setActiveTab('windows')}
            >
              Windows
            </button>
            <button 
              className={`guide-tab-btn ${activeTab === 'macos' ? 'active' : ''}`}
              onClick={() => setActiveTab('macos')}
            >
              macOS
            </button>
            <button 
              className={`guide-tab-btn ${activeTab === 'linux' ? 'active' : ''}`}
              onClick={() => setActiveTab('linux')}
            >
              Linux
            </button>
          </div>

          {activeTab === 'windows' && (
            <div className="steps-list">
              <div className="step-item">
                <span className="step-number">1</span>
                <div className="step-content">
                  <strong>Faça o download do arquivo .exe</strong>
                  <p>Clique no botão de download para obter o <span className="code-snippet">LembreteChaveM-Windows.exe</span>.</p>
                </div>
              </div>
              <div className="step-item">
                <span className="step-number">2</span>
                <div className="step-content">
                  <strong>Execute o aplicativo</strong>
                  <p>Não precisa de direitos de administrador. Basta dar dois cliques no executável.</p>
                </div>
              </div>
              <div className="step-item">
                <span className="step-number">3</span>
                <div className="step-content">
                  <strong>Pronto! Ícone na bandeja</strong>
                  <p>O aplicativo aparecerá ao lado do relógio do Windows. Clique com botão direito nele para configurar horários ou testar notificações.</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'macos' && (
            <div className="steps-list">
              <div className="step-item">
                <span className="step-number">1</span>
                <div className="step-content">
                  <strong>Baixe e descompacte o arquivo .zip</strong>
                  <p>Dê dois cliques no <span className="code-snippet">LembreteChaveM-MacOS.zip</span> para extrair o <span className="code-snippet">LembreteChaveM.app</span>.</p>
                </div>
              </div>
              <div className="step-item">
                <span className="step-number">2</span>
                <div className="step-content">
                  <strong>Mova para Aplicativos</strong>
                  <p>Arraste o aplicativo para a sua pasta de Aplicativos.</p>
                </div>
              </div>
              <div className="step-item">
                <span className="step-number">3</span>
                <div className="step-content">
                  <strong>Primeira abertura (Gatekeeper)</strong>
                  <p>Por ser um app corporativo interno, se o macOS exibir aviso de desenvolvedor não verificado, clique com o botão direito sobre o app e escolha <em>"Abrir"</em>.</p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'linux' && (
            <div className="steps-list">
              <div className="step-item">
                <span className="step-number">1</span>
                <div className="step-content">
                  <strong>Baixe o binário</strong>
                  <p>Salve o arquivo <span className="code-snippet">LembreteChaveM-Linux</span> na sua máquina.</p>
                </div>
              </div>
              <div className="step-item">
                <span className="step-number">2</span>
                <div className="step-content">
                  <strong>Conceda permissão de execução</strong>
                  <p>Abra o terminal e execute:</p>
                  <div className="code-snippet">chmod +x LembreteChaveM-Linux</div>
                </div>
              </div>
              <div className="step-item">
                <span className="step-number">3</span>
                <div className="step-content">
                  <strong>Inicie o programa</strong>
                  <div className="code-snippet">./LembreteChaveM-Linux</div>
                </div>
              </div>
            </div>
          )}

        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <p>© {new Date().getFullYear()} FourSys — Ferramenta interna de automação e produtividade.</p>
          <p>
            Desenvolvido com carinho para os colaboradores. Versão ativa: <strong>{versionData.version}</strong>
          </p>
        </div>
      </footer>
    </div>
  );
}
