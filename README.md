# 🔐 Lembrete Chave M (Foursys • Bradesco)

Um gadget desktop moderno, leve e 100% offline desenvolvido para lembrar os colaboradores da **Foursys** alocados no cliente **Bradesco** sobre o prazo de renovação da senha da **Chave M** antes que ela expire.

---

## 🚀 Regras de Negócio e Funcionalidades

- **🔒 100% Offline e Privado:** Não necessita de conexão com a internet, banco de dados ou APIs. Dados salvos localmente em `~/.foursys_chave_m/config.json`.
- **🛡️ Troca Preventiva (Até o 29º dia):** O dia 30 (expiração) não é considerado aceitável para troca. O prazo limite seguro é sempre até o **29º dia**.
- **📅 Antecipação Inteligente para Dias Úteis (Sábado, Domingo e Feriados):**
  - Se o 29º dia cair em um **sábado**, **domingo** ou **feriado nacional brasileiro** (Tiradentes, Independência, Consciência Negra, Páscoa, Carnaval, etc.), o sistema **antecipa automaticamente** a data limite para o dia útil anterior em que o colaborador esteja trabalhando!
  - Um aviso visual transparente informa quando a data foi antecipada e o motivo.
- **🔔 Alertas Automáticos Gradativos:**
  - ⚠️ **5 dias antes:** Aviso preventivo para agendamento.
  - ⚠️ **3 dias antes:** Alerta de prazo curto.
  - 🚨 **2 dias antes:** Alerta de urgência.
  - 🚨 **1 dia antes (Amanhã):** Alerta crítico (amanhã é o último dia útil).
  - 🚨 **No dia limite (Hoje):** Alerta máximo para troca imediata.
- **🌐 Acesso Direto com 1 Clique ao Portal:**
  - Botão vermelho destacado no app e item no menu da bandeja para abrir diretamente a página de gerenciamento de senha do Bradesco:
    `https://bradesco.identitynow.com/r/default/password-management`
- **🕒 Fica na Bandeja do Sistema (System Tray):** Fica ao lado do relógio do Windows/Mac/Linux sem ocupar a barra de tarefas.
- **⚡ Registro Rápido:** Botão *"Já Troquei Minha Senha Hoje"* para atualizar o ciclo com 1 clique, ou seletor de data manual.
- **🔄 Inicialização Automática:** Opção para iniciar junto com o computador.
- **📦 Executável Portátil:** Arquivo `.exe` independente, sem necessidade de instalar Python.

---

## 📁 Estrutura do Projeto

```
automacao-foursys/
├── assets/
│   ├── icon.png            # Ícone oficial em alta resolução
│   └── icon.ico            # Ícone formatado para Windows
├── src/
│   ├── config.py           # Regras de negócio, prazos e cores visuais
│   ├── holidays.py         # Cálculo offline de feriados nacionais e dias úteis
│   ├── storage.py          # Gerenciamento de persistência local (JSON)
│   ├── reminder_engine.py  # Cálculo de dias restantes, status e limiares
│   ├── notifier.py         # Disparador de notificações nativas do SO
│   ├── autostart.py        # Gerenciador de inicialização no boot
│   ├── tray.py             # Integração com a bandeja do sistema (System Tray)
│   └── gui.py              # Interface gráfica moderna (CustomTkinter)
├── web/                    # Landing page corporativa em Next.js (deploy na Vercel)
│   ├── app/                # Páginas, estilos e endpoint de versão dinâmica
│   └── public/             # Ícones e recursos visuais
├── tests/
│   ├── test_holidays.py    # Testes dos feriados e antecipação de dias úteis
│   ├── test_storage.py     # Testes unitários do armazenamento
│   └── test_reminder_engine.py # Testes dos cálculos de expiração e alertas
├── dist/
│   └── LembreteChaveM.exe  # Executável portátil para Windows (sem dependências)
├── LembreteChaveM_v1.2.0.zip # Pacote pronto para compartilhamento via Teams/Email
├── build_exe.py            # Script PyInstaller para compilação multiplataforma
├── build_exe.bat           # Gerador automático do .exe em 1 clique (Windows)
├── run.bat                 # Atalho para executar via Python em segundo plano
├── main.py                 # Ponto de entrada da aplicação
└── requirements.txt        # Dependências do projeto
```

---

## 🛠️ Como Utilizar

### Compartilhar com Colegas de Equipe
Envie o arquivo [LembreteChaveM_v1.2.0.zip](file:///c:/Projetos/automacao-foursys/LembreteChaveM_v1.2.0.zip). O colaborador só precisa extrair e dar dois cliques no `LembreteChaveM.exe`.

### Rodar em Desenvolvimento (Python)
```bash
.\.venv\Scripts\python main.py
```

### Rodar Todos os Testes
```bash
.\.venv\Scripts\python -m unittest discover tests
```
