import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from livekit.agents import JobContext, JobProcess, Agent, AgentSession, AgentServer, cli, mcp
from livekit.plugins import silero, openai

load_dotenv()

logger = logging.getLogger("mcp-agent")
logger.setLevel(logging.INFO)

MCP_SERVERS = {
    "weather": "http://100.100.108.28:9004/mcp",
    "golden": "http://100.100.108.28:9001/mcp",
    "pop": "http://100.100.108.28:9002/mcp",
    "market": "http://100.100.108.28:9003/mcp",
    "faq-videos": "http://100.100.108.28:9005/mcp"
}

class MyAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You can retrieve data via the MCP server. The interface is voice-based: "
                "accept spoken user queries and respond with synthesized speech."
            ),
        )

    async def on_enter(self, **kwargs):
        await self.session.generate_reply()

server = AgentServer()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

server.setup_fnc = prewarm

@server.rtc_session()
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    # Initialize Whisper STT using OpenAI Plugin
    whisper_stt = openai.STT(
        base_url="http://localhost:8030/v1",
        model="deepdml/faster-whisper-large-v3-turbo-ct2",
        api_key="whisper", 
        language="hi"
    )
    
    # Initialize Ollama LLM using OpenAI Plugin
    ollama_llm = openai.LLM(
        base_url="http://100.100.108.27:11434/v1",
        model="qwen3:32b",
        api_key="ollama", 
    )
    
    # Initialize Kokoro TTS using OpenAI Plugin
    kokoro_tts = openai.TTS(
        base_url="http://localhost:8880/v1",
        model="kokoro",
        # voice="af_bella",
        voice ="hf_alpha",
        api_key="kokoro", 

    )

    # Convert MCP_SERVERS dict to list of MCPServerHTTP
    mcp_servers_list = [mcp.MCPServerHTTP(url=url) for url in MCP_SERVERS.values()]

    # Ensure VAD is loaded (fallback if prewarm didn't run)
    vad_instance = ctx.proc.userdata.get("vad")
    if not vad_instance:
        logger.info("VAD not found in userdata, loading now")
        vad_instance = silero.VAD.load()

    session = AgentSession(
        vad=vad_instance,
        stt=whisper_stt,
        llm=ollama_llm,
        tts=kokoro_tts,
        mcp_servers=mcp_servers_list,
    )

    await session.start(agent=MyAgent(), room=ctx.room)
    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(server)
