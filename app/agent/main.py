from functools import lru_cache

from strands import Agent
from strands.agent.conversation_manager.null_conversation_manager import NullConversationManager
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model
from parse import parse_payload
from memory.session import get_memory_session_manager

DEFAULT_SYSTEM_PROMPT = """Eres el Guionista de AWS Sin Mapa, el proyecto de Oshin Villegas para aprender AWS desde cero.
Escribes guiones cortos para TikTok (30 a 60 segundos) en espanol, con tono cercano, sencillo y ejemplos cotidianos.
Antes de escribir, usa SIEMPRE la herramienta buscar_en_aws_sin_mapa para ver como Oshin ya explico el tema y reutiliza sus ejemplos.
Si no encuentras nada de AWS Sin Mapa sobre el tema, dilo y escribe el guion con informacion general, avisando que no viene de sus guiones.
Estructura: gancho inicial, explicacion con un ejemplo y cierre. Responde solo con el guion.
Oshin es mujer: cuando hables de ella, usa siempre el femenino (ella, la creadora).
Piensa y responde siempre en espanol.
No muestres tus pensamientos ni uses etiquetas <thinking>: entrega solo el guion final.
Termina SIEMPRE el guion con esta frase exacta, sin cambiarla: "Aprende AWS desde 0 conmigo y no te pierdas la próxima clase de AWS Sin Mapa." """

# Define a collection of tools used by the model
tools = []

# Herramienta del agente: busca en la Knowledge Base de AWS Sin Mapa
from kb_tool import buscar_en_aws_sin_mapa
tools.append(buscar_en_aws_sin_mapa)

def _make_conversation_manager():
    return NullConversationManager()

@lru_cache(maxsize=128)
def _get_agent(session_id: str, actor_id: str) -> Agent:
    """Given a session_id and actor_id, return or construct the corresponding Strands agent.
    Note: caching helps avoid repeated identity fetches on non-bedrock model loads
    and supports in-memory session management for local dev."""
    return Agent(
        model=load_model(),
        session_manager=get_memory_session_manager(session_id, actor_id),
        conversation_manager=_make_conversation_manager(),
        system_prompt=DEFAULT_SYSTEM_PROMPT,
        tools=tools,
    )

def create_app():
    app = BedrockAgentCoreApp()
    log = app.logger

    @app.entrypoint
    async def invoke(payload, context):
        log.info("Invoking Agent.....")

        session_id = getattr(context, "session_id", None) or "default-session"
        prompt, actor_id = parse_payload(payload)

        log.info(f"Invoking with session_id={session_id} and actor_id={actor_id}")
        agent = _get_agent(session_id, actor_id)

        async for event in agent.stream_async(prompt):
            if not isinstance(event, dict) or "event" not in event:
                continue
            cbs = event["event"].get("contentBlockStart")
            if cbs is not None and not cbs.get("start"):
                continue
            yield event

    return app

app = create_app()
if __name__ == "__main__":
    app.run()
