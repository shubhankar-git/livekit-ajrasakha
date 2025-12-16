## Brief Documentation

A **LiveKit-based voice agent** enabling real-time spoken interaction with **MCP tool access**.

### Flow
- Live audio enters a LiveKit room  
- Silero VAD detects speech  
- Whisper (self-hosted) converts speech to text  
- Qwen-32B (Ollama) reasons and calls MCP tools if needed  
- Kokoro TTS converts text to speech  
- Audio response is streamed back to the user  

### Core Features
- Fully self-hosted STT, LLM, and TTS  
- OpenAI-compatible APIs  
- Dynamic tool usage via multiple MCP HTTP servers  
- Low-latency, interruptible voice conversations  

### Key Components
- **AgentServer** – manages RTC sessions  
- **AgentSession** – connects VAD, STT, LLM, TTS, MCP  
- **MyAgent** – defines system instructions  
- **MCP Servers** – weather, market, FAQ, etc.  

### Outcome
A production-ready **real-time voice + tools agent** with no cloud lock-in.
