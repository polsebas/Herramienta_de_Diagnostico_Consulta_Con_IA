# Progress Report – Herramienta de Diagnóstico y Consulta con IA

Este documento registra el estado actual del proyecto, los objetivos de mejora con **ingeniería de contexto**, y el plan de implementación en fases para convertir la herramienta en un sistema escalable y robusto de diagnóstico y consulta.

---

## 🔎 Estado Actual (agosto 2025)

- **Stack**:  
  - Python 3.11+  
  - Milvus Lite (vector DB)  
  - SentenceTransformers (`all-MiniLM-L6-v2`)  
  - Async Agents (con flags `use_tools`, `show_tool_calls`)  

- **Funcionalidad actual**:  
  - Procesamiento automático de `.md` en `knowledge_base/`  
  - Indexación en Milvus  
  - RAG básico: recuperación semántica + respuesta LLM  
  - Uso típico: consultas técnicas ("¿Cómo funciona el sistema de pagos?")  

- **Limitaciones**:  
  - Sin contratos/specs → riesgo de respuestas vagas  
  - Contexto crece sin control → alucinaciones en multi-turno  
  - Recuperación solo vectorial, sin rerank ni filtros  
  - Sin subagentes (todo centralizado en `Agent`)  
  - Sin evaluación automatizada de calidad ni métricas  

---

## 🚀 Objetivo “Next Level”

Aplicar el workflow **Research → Plan → Implement**, con:

1. **Spec-first development**  
   - Cada query se transforma en un contrato de tarea (objetivos, restricciones, formato).  
2. **Compactación intencional**  
   - Resumir historial y chunks → <40% de la ventana del modelo.  
3. **Subagentes especializados**  
   - Retrieval, Analysis, Synthesis, Verification.  
4. **Recuperación avanzada**  
   - Híbrido BM25 + vector + rerank, con metadatos enriquecidos.  
5. **Guardrails**  
   - Citas obligatorias, suposiciones explícitas, checklist de formato.  
6. **Evaluación continua**  
   - Golden set de queries, compliance con contrato, recall, latencia, tokens.  
7. **Entrega práctica**  
   - CLI (`ragc`) y API (FastAPI).  

---

## 📂 Nueva Organización del Repo

app/
├─ spec_layer.py
├─ context_manager.py
├─ subagents/
│ ├─ retrieval.py
│ ├─ analysis.py
│ ├─ synthesis.py
│ └─ verification.py
├─ retrieval/
│ ├─ splitters.py
│ ├─ hybrid.py
│ ├─ rerank.py
│ └─ store_milvus.py
├─ prompts/
│ ├─ retrieval.md
│ ├─ analyze.md
│ ├─ synthesis.md
│ └─ verification.md
├─ eval/
│ ├─ evaluate_contract_compliance.py
│ ├─ measure_token_usage.py
│ └─ benchmark_retrieval.py
├─ api/server.py
└─ cli.py
docs/
├─ CONTRATOS.md
└─ PLAYBOOKS.md
tests/
logs/
└─ context_stats.jsonl


---

## 📌 Roadmap de PRs

### PR-1 → Spec-first Layer
- [ ] Crear `app/spec_layer.py` con `TaskContract`  
- [ ] Hook en `Agent` para generar contrato antes de responder  
- [ ] Documentar en `docs/CONTRATOS.md`  

### PR-2 → Compactación
- [ ] Implementar `app/context_manager.py` (resumen de historial y chunks)  
- [ ] Logging de tokens (usar `tiktoken`)  
- [ ] Guardar en `logs/context_stats.jsonl`  

### PR-3 → Recuperación avanzada
- [ ] `retrieval/hybrid.py`: merge vector + BM25  
- [ ] `rerank.py`: usar modelo re-ranker local (`bge-reranker-base`)  
- [ ] `splitters.py`: chunking semántico (por títulos Markdown)  
- [ ] `store_milvus.py`: esquema con metadatos (doc_id, title, section, line_start/end, updated_at)  

### PR-4 → Subagentes
- [ ] `subagents/retrieval.py`: búsqueda híbrida  
- [ ] `subagents/analysis.py`: clusterización, detección de huecos  
- [ ] `subagents/synthesis.py`: redacción según contrato  
- [ ] `subagents/verification.py`: checklist de cumplimiento  

### PR-5 → Evaluación
- [ ] Crear `eval/` con golden set de 20–40 queries reales  
- [ ] Script `evaluate_contract_compliance.py` → compliance %  
- [ ] Script `benchmark_retrieval.py` → Recall@k, nDCG@k  
- [ ] Script `measure_token_usage.py` → reducción promedio  

### PR-6 → CLI + API
- [ ] CLI `ragc`:  
  - `ragc ask "..." --format md`  
  - `ragc index ./knowledge_base`  
- [ ] FastAPI con endpoints `/ask`, `/health`, `/metrics`  

---

## 📊 Métricas de Progreso

| Métrica                 | Baseline | Meta Next Level |
|--------------------------|----------|-----------------|
| **Contract compliance** | ~40–50% | ≥80% |
| **Tokens por prompt**   | 100%    | −30% |
| **Recall@5**            | ~60%    | +20% |
| **Latencia p95**        | 1.0x    | −20% |
| **Alucinaciones**       | Alta    | −50% |

---

## ✅ Estado de Avances

- [x] RAG inicial con Milvus Lite + embeddings.  
- [ ] Spec layer (contratos YAML/Markdown).  
- [ ] Compactación de contexto.  
- [ ] Subagentes modulares.  
- [ ] Recuperación híbrida con rerank.  
- [ ] Evaluación continua (golden set).  
- [ ] CLI + FastAPI.  

---

## 🔮 Próximos pasos inmediatos

1. Implementar **PR-1 (spec_layer.py)**.  
2. Correr baseline: 20 queries → medir precisión, tokens y longitud de respuestas.  
3. Documentar contratos de ejemplo en `docs/CONTRATOS.md`.  

---
