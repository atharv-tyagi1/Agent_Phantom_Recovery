# Contributing to Agent Phantom Recovery

Thank you for your interest in contributing to **Agent Phantom Recovery**! We welcome contributions from developers, researchers, and open-source enthusiasts.

---

## 📜 Code of Conduct

We are committed to providing a welcoming, inclusive, and harassment-free experience for everyone. Please be respectful and professional in all communications.

---

## 🛠 Local Setup & Development Workflow

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/Agent_Phantom_Recovery.git
cd Agent_Phantom_Recovery
```

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
> [!WARNING]
> Never commit `.env` or `.env.local` files! All secrets must remain local.

### 3. Backend Setup
```bash
cd services/api
python -m venv venv
venv\Scripts\activate  # On Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
```

### 4. Running Tests & Gate Checks
Before submitting a PR, ensure all unit tests and release gate assertions pass:
```bash
# Run backend test suite
set PYTHONPATH=services/api
python -m pytest services/api/tests/

# Run automated release gate
python services/api/scripts/production_readiness_gate.py
```

### 5. Frontend Setup
```bash
cd apps/web
npm install
npm run dev
```

---

## 🔀 Pull Request Process

1. Create a feature branch off `main`: `git checkout -b feat/your-feature-name`.
2. Write clean, self-documenting code with type hints.
3. Verify zero secrets are staged (`git status --ignored`).
4. Ensure 100% Pytest assertions and TypeScript compilation check (`npx tsc --noEmit`) pass.
5. Push to your fork and submit a Pull Request describing your changes.

Thank you for helping build the future of autonomous engineering!
