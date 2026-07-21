from core.config import settings

# OpenRouter Base
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY

# Zenmux Base
ZENMUX_BASE_URL = "https://api.zenmux.com/v1" # Assuming standard v1/chat/completions endpoint
ZENMUX_API_KEY = settings.ZENMUX_API_KEY

# Primary Model: Planner & Reasoner (via Zenmux)
PRIMARY_MODEL = "moonshot-v1-auto"

# Fallback Model: Planner & Reasoner (via OpenRouter)
FALLBACK_MODEL = "tencent/hunyuan-pro"

# Verifier Model: Independent gatekeeper (via OpenRouter)
VERIFIER_MODEL = "nvidia/llama-3.1-nemotron-70b-instruct:free"

HEADERS = {
    "HTTP-Referer": "http://localhost:3000",
    "X-Title": "Agent Phantom Recovery",
}
