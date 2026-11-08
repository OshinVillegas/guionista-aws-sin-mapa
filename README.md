# 🎬 Guionista de AWS Sin Mapa — mi primer agente de IA en AWS

> Un agente que escribe guiones de TikTok usando **mis propios guiones** como fuente.
> Hecho con **Amazon Bedrock AgentCore**, **Strands Agents** y la Knowledge Base de mi [primer RAG](https://github.com/OshinVillegas/mi-primer-rag-aws).
> Parte de la serie **IA desde 0** de AWS Sin Mapa. 💪

## 🤔 ¿Qué diferencia hay entre un RAG y un agente?

| | RAG (proyecto 1) | Agente (este proyecto) |
|---|---|---|
| Qué hace | Responde preguntas | **Crea algo nuevo**: un guion listo para grabar |
| ¿Quién decide buscar? | El código, siempre | **El agente decide** cuándo usar su herramienta |
| Memoria | No | **Sí**: recuerda la conversación |

Un chat **responde**. Un agente **responde y hace cosas**: tiene **herramientas** y **memoria**, y decide cuándo usarlas.

## 🏗️ Arquitectura

```
Tú → agentcore invoke → AgentCore Runtime (agente Guionista, Strands)
                              │
                              ├─ 🧠 Amazon Nova Lite (el modelo)
                              ├─ 🔧 Herramienta buscar_en_aws_sin_mapa → Knowledge Base (mis guiones en S3)
                              └─ 💾 AgentCore Memory (recuerda la conversación)
```

## 📁 Qué hay en el repo

| Archivo | Para qué sirve |
|---|---|
| `app/agent/main.py` | El agente: sus instrucciones (personalidad) y su caja de herramientas |
| `app/agent/kb_tool.py` | La herramienta que busca en la Knowledge Base (es el `retrieve` del RAG, con `@tool`) |
| `app/agent/model/load.py` | El modelo que usa: Amazon Nova Lite |
| `app/agent/memory/session.py` | La memoria del agente (AgentCore Memory) |
| `agentcore/agentcore.json` | La configuración del proyecto para AgentCore |
| `pedir_guion.sh` | Ayudante para pedir un guion y ver la respuesta limpia |
| `iam-policy.json` | El permiso mínimo que necesita el agente |

## 🚀 Paso a paso

Todo lo hice en **AWS CloudShell**, en la región **us-east-1**.

### 1. Necesitas
- Una Knowledge Base de Amazon Bedrock con tus documentos (mira mi [primer RAG](https://github.com/OshinVillegas/mi-primer-rag-aws)).
- Acceso a **Amazon Nova Lite** en Bedrock.

### 2. Instala las herramientas
```
pip3 install uv && sudo npm install -g @aws/agentcore
```

### 3. Clona el repo y pon el ID de tu Knowledge Base
En `app/agent/kb_tool.py`, cambia `TU_KNOWLEDGE_BASE_ID` por el ID de tu Knowledge Base.

### 4. Pruébalo en tu CloudShell
```
agentcore dev
```
En otra pestaña:
```
curl -X POST http://localhost:8080/invocations -H "Content-Type: application/json" -d '{"prompt": "Escribe un guion de TikTok sobre los grupos IAM"}'
```

### 5. Publícalo en la nube (AgentCore Runtime)
```
agentcore deploy
```

### 6. Dale el permiso mínimo 🔒
En la nube, el agente tiene **su propio rol de IAM**, y ese rol no puede leer tu Knowledge Base hasta que se lo permitas. Busca el rol:
```
aws iam list-roles --query "Roles[?contains(RoleName,'Guionista') && contains(RoleName,'Runtime')].RoleName" --output text
```
Y agrégale la política de `iam-policy.json` (con tu número de cuenta y el ID de tu Knowledge Base): **solo `bedrock:Retrieve`, solo en tu Knowledge Base**.

### 7. Pide un guion
```
chmod +x pedir_guion.sh
./pedir_guion.sh los grupos IAM
```

## 🧪 Lo que hace el agente

Le pedí *"Escribe un guion de TikTok sobre los grupos IAM"* y:
1. **Decidió solo** usar su herramienta: *"Primero, buscaré en AWS Sin Mapa…"*.
2. Encontró mi guion del Video 23 en la Knowledge Base.
3. Escribió un guion nuevo con **mis ejemplos**: María, Pedro, Ana y Juan en el grupo "Desarrolladores".
4. Terminó con mi frase: *"Aprende AWS desde 0 conmigo y no te pierdas la próxima clase de AWS Sin Mapa."*

## 🐞 Errores que tuve (y cómo los resolví)

- **El modelo del ejemplo no estaba disponible en mi cuenta** (`AccessDeniedException`). Lo cambié por Amazon Nova Lite en `model/load.py`.
- **En la nube, la herramienta fallaba** pero en CloudShell funcionaba. Era el permiso: el rol del agente no podía leer la Knowledge Base. Lo resolví con una política de **mínimo privilegio**.
- **La memoria recordaba el error:** después de dar el permiso, el agente no volvía a intentar usar la herramienta porque "recordaba" que había fallado. Tuve que pedírselo explícitamente.
- **Nova Lite muestra sus pensamientos** (`<thinking>`) aunque le pida que no. Los limpio con `pedir_guion.sh`.

## ✅ Buenas prácticas de AI Engineering

- **Mínimo privilegio:** el agente solo puede buscar, y solo en una Knowledge Base.
- **Honestidad:** si la herramienta falla, el agente avisa que el guion no viene de mis guiones.
- **Instrucciones claras:** personalidad, estructura del guion y frase de cierre en el *system prompt*.
- **Medir:** tokens y latencia en cada respuesta.

## 🧹 Cómo borrar todo

```
agentcore remove all --yes
agentcore deploy --yes
```

---

Hecho por **Oshin Villegas** como parte de **AWS Sin Mapa · IA desde 0**.
*"APRENDE AWS DESDE 0 CONMIGO Y NO TE PIERDAS LA PROXIMA CLASE DE AWS SIN MAPA."*
