import './globals.css';

export const metadata = {
  title: 'Lembrete Chave M | FourSys',
  description: 'Aplicativo corporativo para garantir o preenchimento diário da Chave M sem esquecimentos. Disponível para Windows, macOS e Linux.',
  icons: {
    icon: '/icon.png',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <head>
        <link rel="icon" href="/icon.png" type="image/png" />
      </head>
      <body>{children}</body>
    </html>
  );
}
