# Windows installation guide

## Requirements

- Windows 10 or 11
- 8 GB RAM recommended, 16 GB preferred for smoother local generation
- NVIDIA GPU preferred for faster inference, but CPU-only operation is supported for lighter work
- Python 3.11+
- Node.js 20+
- Rust toolchain for Tauri builds

## 1. Install dependencies

```powershell
winget install Python.Python.3.11
winget install OpenJS.NodeJS.LTS
winget install Rustlang.Rustup
```

## 2. Clone repository

```powershell
git clone https://github.com/forotherwork786-stack/ai-studio.git
cd ai-studio
```

## 3. Frontend

```powershell
cd apps\desktop
npm install
npm run dev
```

## 4. Backend

```powershell
cd ..\..\services\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 5. Optional Tauri desktop build

```powershell
cd apps\desktop
npm install
cargo install tauri-cli
cargo tauri dev
```

## 6. Recommendations

- Use Low Resource mode on systems with less than 16 GB RAM
- Prefer Stable Diffusion 1.5 for first local image generation
- Keep model downloads in a dedicated local models directory
- Test hardware compatibility before enabling large batch generation
