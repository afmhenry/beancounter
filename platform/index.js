// https://github.com/electron/electron/blob/main/docs/tutorial/quick-start.md
const { app, BrowserWindow } = require('electron')
const path = require('path')
const server = require('./server');

const createWindow = () => {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })
  //win.loadFile('index.html')
  win.webContents.openDevTools()
  win.loadURL('http://localhost:3000/');

}

app.whenReady().then(() => {
  createWindow()
  //if no windows on mac, but still running, make a new one.
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

//kill process if window closed
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})
