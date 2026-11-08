import os
import boto3
from strands import tool

# ID de tu Knowledge Base (Bedrock > Bases de conocimientos)
KB_ID = os.getenv("KB_ID", "TU_KNOWLEDGE_BASE_ID")
kb = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

@tool
def buscar_en_aws_sin_mapa(tema: str) -> str:
    """Busca en los guiones de AWS Sin Mapa lo que Oshin ya explico sobre un tema de AWS.
    Usala SIEMPRE antes de escribir un guion, para usar sus ejemplos y su forma de explicar.

    Args:
        tema: el tema a buscar, por ejemplo "grupos IAM" o "cloud computing".
    """
    resultados = kb.retrieve(knowledgeBaseId=KB_ID, retrievalQuery={"text": tema})
    pedazos = []
    for r in resultados["retrievalResults"]:
        fuente = r["location"].get("s3Location", {}).get("uri", "desconocida")
        pedazos.append(f"[Fuente: {fuente}]\n{r['content']['text']}")
    if not pedazos:
        return "No encontre nada sobre ese tema en los guiones de AWS Sin Mapa."
    return "\n\n".join(pedazos)
