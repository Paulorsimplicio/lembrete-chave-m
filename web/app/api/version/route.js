import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';
export const revalidate = 0;

export async function GET() {
  const repo = 'Paulorsimplicio/lembrete-chave-m';
  const defaultVersion = 'v1.4.2';
  
  const defaultAssets = {
    windows: {
      name: 'LembreteChaveM-Windows.zip',
      url: `https://github.com/${repo}/releases/latest/download/LembreteChaveM-Windows.zip`,
      os: 'Windows'
    },
    macos: {
      name: 'LembreteChaveM-MacOS.zip',
      url: `https://github.com/${repo}/releases/latest/download/LembreteChaveM-MacOS.zip`,
      os: 'macOS'
    },
    linux: {
      name: 'LembreteChaveM-Linux.zip',
      url: `https://github.com/${repo}/releases/latest/download/LembreteChaveM-Linux.zip`,
      os: 'Linux'
    },
    manual: {
      name: 'Manual_de_Uso.html',
      url: `/Manual_de_Uso.html`
    }
  };

  try {
    const headers = {
      'Accept': 'application/vnd.github.v3+json',
      'User-Agent': 'FourSys-LembreteChaveM-Web'
    };

    if (process.env.GITHUB_TOKEN) {
      headers['Authorization'] = `Bearer ${process.env.GITHUB_TOKEN}`;
    }

    const res = await fetch(`https://api.github.com/repos/${repo}/releases/latest`, {
      headers,
      cache: 'no-store'
    });

    if (!res.ok) {
      return NextResponse.json({
        success: true,
        version: defaultVersion,
        publishedAt: null,
        notes: 'Versão estável mais recente.',
        assets: defaultAssets
      }, {
        headers: {
          'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate'
        }
      });
    }

    const data = await res.json();
    const assets = { ...defaultAssets };

    if (Array.isArray(data.assets)) {
      data.assets.forEach(asset => {
        const nameLower = asset.name.toLowerCase();
        if (nameLower.includes('manual')) {
          assets.manual = {
            name: asset.name,
            url: asset.browser_download_url
          };
        } else if (nameLower.includes('windows')) {
          if (nameLower.endsWith('.zip')) {
            const isVersioned = nameLower.includes('-v');
            if (!assets.windows.isVersioned || isVersioned) {
              assets.windows = {
                name: asset.name,
                url: asset.browser_download_url,
                size: asset.size,
                os: 'Windows',
                isVersioned
              };
            }
          }
        } else if (nameLower.includes('mac')) {
          if (nameLower.endsWith('.zip')) {
            const isVersioned = nameLower.includes('-v');
            if (!assets.macos.isVersioned || isVersioned) {
              assets.macos = {
                name: asset.name,
                url: asset.browser_download_url,
                size: asset.size,
                os: 'macOS',
                isVersioned
              };
            }
          }
        } else if (nameLower.includes('linux')) {
          if (nameLower.endsWith('.zip')) {
            const isVersioned = nameLower.includes('-v');
            if (!assets.linux.isVersioned || isVersioned) {
              assets.linux = {
                name: asset.name,
                url: asset.browser_download_url,
                size: asset.size,
                os: 'Linux',
                isVersioned
              };
            }
          }
        }
      });
    }

    return NextResponse.json({
      success: true,
      version: data.tag_name || defaultVersion,
      publishedAt: data.published_at || null,
      notes: data.body || 'Melhorias de desempenho e correções automáticas.',
      assets
    }, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate'
      }
    });
  } catch (err) {
    return NextResponse.json({
      success: true,
      version: defaultVersion,
      publishedAt: null,
      notes: 'Versão padrão para download.',
      assets: defaultAssets
    }, {
      headers: {
        'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate'
      }
    });
  }
}
