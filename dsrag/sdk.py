from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from dsrag.config.schema import CONFIG_SCHEMA_VERSION
from dsrag.diagnostics import run_diagnostics


SDK_SCHEMA_VERSION = "1.0"


@dataclass
class CreateKBRequest:
    kb_id: str
    profile: str = "general_balanced"
    title: str = ""
    supp_id: str = ""
    description: str = ""
    language: str = "en"
    storage_directory: str = "~/dsRAG"
    exists_ok: bool = True
    telemetry_sink: Any = None


@dataclass
class AddDocumentRequest:
    kb_id: str
    doc_id: str
    text: str = ""
    file_path: str = ""
    document_title: str = ""
    auto_context_config: Optional[Dict[str, Any]] = None
    file_parsing_config: Optional[Dict[str, Any]] = None
    semantic_sectioning_config: Optional[Dict[str, Any]] = None
    chunking_config: Optional[Dict[str, Any]] = None
    chunk_size: Optional[int] = None
    min_length_for_chunking: Optional[int] = None
    supp_id: str = ""
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class QueryRequest:
    kb_id: str
    search_queries: List[str]
    rse_params: Optional[Any] = None
    latency_profiling: bool = False
    metadata_filter: Optional[Dict[str, Any]] = None
    return_mode: str = "text"
    vector_search_top_k: Optional[int] = None


@dataclass
class ExportConfigRequest:
    kb_id: str
    include_sensitive: bool = False


@dataclass
class GetTelemetryRequest:
    kb_id: str


def _get_kb_class():
    from dsrag.knowledge_base import KnowledgeBase

    return KnowledgeBase


def _response_ok(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_version": SDK_SCHEMA_VERSION,
        "ok": True,
        "data": data,
    }


def _error_code_for_exception(exc: Exception) -> str:
    if isinstance(exc, ValueError):
        return "INVALID_ARGUMENT"
    if isinstance(exc, FileNotFoundError):
        return "NOT_FOUND"
    return "INTERNAL_ERROR"


def _response_error(exc: Exception) -> Dict[str, Any]:
    return {
        "schema_version": SDK_SCHEMA_VERSION,
        "ok": False,
        "error": {
            "code": _error_code_for_exception(exc),
            "message": str(exc),
        },
    }


class DSRAGSDK:
    def __init__(self):
        self._knowledge_bases: Dict[str, Any] = {}

    def _get_or_load_kb(self, kb_id: str):
        if kb_id in self._knowledge_bases:
            return self._knowledge_bases[kb_id]
        kb_cls = _get_kb_class()
        kb = kb_cls(kb_id=kb_id, exists_ok=True)
        self._knowledge_bases[kb_id] = kb
        return kb

    def create_kb(self, request: CreateKBRequest) -> Dict[str, Any]:
        try:
            kb_cls = _get_kb_class()
            kb = kb_cls(
                kb_id=request.kb_id,
                profile=request.profile,
                title=request.title,
                supp_id=request.supp_id,
                description=request.description,
                language=request.language,
                storage_directory=request.storage_directory,
                exists_ok=request.exists_ok,
                telemetry_sink=request.telemetry_sink,
            )
            self._knowledge_bases[request.kb_id] = kb
            return _response_ok(
                {
                    "kb_id": request.kb_id,
                    "profile": request.profile,
                    "created": True,
                }
            )
        except Exception as exc:
            return _response_error(exc)

    def add_document(self, request: AddDocumentRequest) -> Dict[str, Any]:
        try:
            kb = self._get_or_load_kb(request.kb_id)
            kb.add_document(
                doc_id=request.doc_id,
                text=request.text,
                file_path=request.file_path,
                document_title=request.document_title,
                auto_context_config=request.auto_context_config,
                file_parsing_config=request.file_parsing_config,
                semantic_sectioning_config=request.semantic_sectioning_config,
                chunking_config=request.chunking_config,
                chunk_size=request.chunk_size,
                min_length_for_chunking=request.min_length_for_chunking,
                supp_id=request.supp_id,
                metadata=request.metadata,
            )
            return _response_ok(
                {
                    "kb_id": request.kb_id,
                    "doc_id": request.doc_id,
                    "added": True,
                }
            )
        except Exception as exc:
            return _response_error(exc)

    def query(self, request: QueryRequest) -> Dict[str, Any]:
        try:
            kb = self._get_or_load_kb(request.kb_id)
            results = kb.query(
                search_queries=request.search_queries,
                rse_params=request.rse_params,
                latency_profiling=request.latency_profiling,
                metadata_filter=request.metadata_filter,
                return_mode=request.return_mode,
                vector_search_top_k=request.vector_search_top_k,
            )
            return _response_ok(
                {
                    "kb_id": request.kb_id,
                    "search_queries": request.search_queries,
                    "results": results,
                    "result_count": len(results),
                }
            )
        except Exception as exc:
            return _response_error(exc)

    def export_config(self, request: ExportConfigRequest) -> Dict[str, Any]:
        try:
            kb = self._get_or_load_kb(request.kb_id)
            config = kb.export_config_schema(include_sensitive=request.include_sensitive)
            return _response_ok(
                {
                    "kb_id": request.kb_id,
                    "config_schema_version": CONFIG_SCHEMA_VERSION,
                    "config": config,
                }
            )
        except Exception as exc:
            return _response_error(exc)

    def run_diagnostics(self) -> Dict[str, Any]:
        try:
            report = run_diagnostics()
            return _response_ok({"report": report})
        except Exception as exc:
            return _response_error(exc)

    def get_telemetry(self, request: GetTelemetryRequest) -> Dict[str, Any]:
        try:
            kb = self._get_or_load_kb(request.kb_id)
            sink = getattr(kb, "telemetry_sink", None)
            if sink is None or not hasattr(sink, "get_events"):
                raise ValueError(
                    "Telemetry sink does not support event retrieval. "
                    "Use InMemoryTelemetrySink to read events."
                )
            events = sink.get_events()
            return _response_ok(
                {
                    "kb_id": request.kb_id,
                    "events": events,
                    "event_count": len(events),
                }
            )
        except Exception as exc:
            return _response_error(exc)
