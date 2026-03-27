const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 900,
    minWidth: 800,
    minHeight: 600,
    title: 'Ollama Chatbot',
    backgroundColor: '#f3efe9',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      webSecurity: true
    },
    show: false // Pokaż dopiero jak się załaduje
  });

  win.loadFile(path.join(__dirname, '../renderer/index.html'));

  // Pokaż okno jak się załaduje (unikamy białego błysku)
  win.once('ready-to-show', () => {
    win.show();
  });

  // DevTools - odkomentuj jeśli chcesz debugować
  // win.webContents.openDevTools();
}

// Menu bar
const template = [
  {
    label: 'Plik',
    submenu: [
      {
        label: 'Zamknij',
        accelerator: 'CmdOrCtrl+W',
        role: 'close'
      },
      {
        label: 'Zakończ',
        accelerator: 'CmdOrCtrl+Q',
        role: 'quit'
      }
    ]
  },
  {
    label: 'Edycja',
    submenu: [
      { label: 'Cofnij', accelerator: 'CmdOrCtrl+Z', role: 'undo' },
      { label: 'Ponów', accelerator: 'Shift+CmdOrCtrl+Z', role: 'redo' },
      { type: 'separator' },
      { label: 'Wytnij', accelerator: 'CmdOrCtrl+X', role: 'cut' },
      { label: 'Kopiuj', accelerator: 'CmdOrCtrl+C', role: 'copy' },
      { label: 'Wklej', accelerator: 'CmdOrCtrl+V', role: 'paste' },
      { label: 'Zaznacz wszystko', accelerator: 'CmdOrCtrl+A', role: 'selectAll' }
    ]
  },
  {
    label: 'Widok',
    submenu: [
      { label: 'Przeładuj', accelerator: 'CmdOrCtrl+R', role: 'reload' },
      { label: 'Narzędzia deweloperskie', accelerator: 'F12', role: 'toggleDevTools' },
      { type: 'separator' },
      { label: 'Pełny ekran', accelerator: 'F11', role: 'togglefullscreen' }
    ]
  }
];

const menu = Menu.buildFromTemplate(template);
Menu.setApplicationMenu(menu);

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});