import { NextResponse } from 'next/server';

export const revalidate = 600; // Cache por 10 minutos

export async function GET() {
  const repo = 'Paulorsimplicio/lembrete-chave-m';
  const defaultVersion = 'v1.2.1';
  
  const defaultAssets = {
    windows: {
      name: 'LembreteChaveM-Windows.exe',
      url: `https://github.com/${repo}/releases/latest/download/LembreteChaveM-Windows.exe`,
      os: 'Windows'
    },
    macos: {
      name: 'LembreteChaveM-MacOS.zip',
      url: `https://github.com/${repo}/releases/latest/download/LembreteChaveM-MacOS.zip`,
      os: 'macOS'
    },
    linux: {
      name: 'LembreteChaveM-Linux',
      url: `https://github.com/${repo}/releases/latest/download/LembreteChaveM-Linux`,
      os: 'Linux'
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
      next: { revalidate: 600 }
    });

    if (!res.ok) {
      return NextResponse.json({
        success: true,
        version: defaultVersion,
        publishedAt: null,
        notes: 'Versão estável mais recente.',
        assets: defaultAssets
      });
    }

    const data = await res.json();
    const assets = { ...defaultAssets };

    if (Array.isArray(data.assets)) {
      data.assets.forEach(asset => {
        if (asset.name.toLowerCase().includes('windows') || asset.name.endsWith('.exe')) {
          assets.windows = {
            name: asset.name,
            url: asset.browser_download_url,
            size: asset.size,
            os: 'Windows'
          };
        } else if (asset.name.toLowerCase().includes('mac') || asset.name.endsWith('.dmg') || asset.name.endsWith('.zip')) {
          assets.macos = {
            name: asset.name,
            url: asset.browser_download_url,
            size: asset.size,
            os: 'macOS'
          };
        } else if (asset.name.toLowerCase().includes('linux')) {
          assets.linux = {
            name: asset.name,
            url: asset.browser_download_url,
            size: asset.size,
            os: 'Linux'
          };
        }
      });
    }

    return NextResponse.json({
      success: true,
      version: data.tag_name || defaultVersion,
      publishedAt: data.published_at || null,
      notes: data.body || 'Melhorias de desempenho e correções automáticas.',
      assets
    });
  } catch (err) {
    return NextResponse.json({
      success: true,
      version: defaultVersion,
      publishedAt: null,
      notes: 'Versão padrão para download.',
      assets: defaultAssets
    });
  }
}
