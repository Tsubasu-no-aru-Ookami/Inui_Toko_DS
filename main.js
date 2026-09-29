const { app, BrowserWindow } = require('electron')
const WebSocket = require('ws')

let win
let ws

function createWindow() {
    win = new BrowserWindow({
        width: 350,
        height: 600,
        x: 5,
        y: 5,
        frame: false,
        alwaysOnTop: true,
        transparent: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    })

    win.loadFile('index.html')
    setupWebSocket()
}

function setupWebSocket() {
    ws = new WebSocket('ws://localhost:8765')

    ws.on('open', () => {
        console.log('Connected to Python server')
        win.webContents.send('status', 'connected')
    })

    ws.on('message', (data) => {
        try {
            const message = JSON.parse(data)
            win.webContents.send('update', message.users)
        } catch (e) {
            console.error('Error parsing message:', e)
        }
    })

    ws.on('error', (err) => {
        console.error('WebSocket error:', err)
        win.webContents.send('status', 'disconnected')
        setTimeout(setupWebSocket, 3000)
    })

    ws.on('close', () => {
        console.log('WebSocket closed')
        win.webContents.send('status', 'disconnected')
        setTimeout(setupWebSocket, 3000)
    })
}

app.whenReady().then(createWindow)