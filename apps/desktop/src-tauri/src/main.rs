{
  "$schema": "https://schema.tauri.app/config/2.0.0",
  "identifier": "com.ai-studio.app",
  "productName": "AI Studio",
  "version": "0.1.0",
  "build": {
    "beforeDevCommand": "npm run dev -- --host 0.0.0.0",
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [
      {
        "title": "AI Studio",
        "width": 1440,
        "height": 980,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "category": "Utility",
    "copyright": "MIT",
    "targets": "all",
    "icon": []
  }
}
