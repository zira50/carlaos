const { app, BrowserWindow } = require('electron');
const { execFile, exec } = require('child_process');
const path = require('path');
const http = require('http');
const fs = require('fs');

console.log("🔥 Electron arrancando...");

let win;
let backend;

const isDev = !app.isPackaged;

// 📍 Ruta del backend
const exePath = isDev
    ? path.join(__dirname, '..', 'dist', 'app.exe')
    : path.join(process.resourcesPath, 'app.exe');

console.log("📦 Ejecutando:", exePath);
console.log("📂 Existe exe:", fs.existsSync(exePath));

function createWindow() {
    win = new BrowserWindow({
        width: 1200,
        height: 800
    });

    win.loadURL('http://127.0.0.1:5000');

    win.on('closed', killBackend);
}

function killBackend() {
    if (backend) {
        backend.kill();
        exec(`taskkill /pid ${backend.pid} /f /t`);
    }
}

// ⏳ Esperar a Flask
function waitForServer(retries = 40) {
    http.get('http://127.0.0.1:5000', () => {
        console.log("✅ Flask listo");
        createWindow();
    }).on('error', () => {
        if (retries > 0) {
            setTimeout(() => waitForServer(retries - 1), 500);
        } else {
            console.error("❌ Flask no respondió");
        }
    });
}

app.whenReady().then(() => {

    console.log("🚀 Lanzando backend...");

    backend = execFile(exePath, [], {
        env: {
            ...process.env,
            ELECTRON: "true"
        }
    });

    backend.stdout?.on('data', (data) => {
        console.log(`🐍 ${data}`);
    });

    backend.stderr?.on('data', (data) => {
        console.error(`💥 ${data}`);
    });

    waitForServer();
});

app.on('window-all-closed', () => {
    killBackend();
    app.quit();
});