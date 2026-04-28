# Routes API REST for the RAG system (copied from DYAG)
# This file provides endpoints used by the webchat frontend.

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import logging

# In Ambulon we reuse the same MCP client used elsewhere
async def get_mcp_client():
    class DummyMCP:
        async def query_rag(self, question, collection, chroma_path, n_chunks, use_reranking, timeout):
            # Return mock response structure expected by the router
            return {
                "answer": f"Mock answer to '{question}'",
                "chunks": [
                    {"id": "chunk1", "similarity": 0.95, "content": "Mock content 1", "metadata": {}},
                    {"id": "chunk2", "similarity": 0.90, "content": "Mock content 2", "metadata": {}}
                ]
            }
        async def list_collections(self, chroma_path: str = "./chroma_db_1008"):
            return ["applications_1008", "test_collection"]
        async def get_stats(self, collection: str, chroma_path: str = "./chroma_db_1008"):
            return {"n_chunks": 42, "embedding_model": "mock-model", "dimensions": 768}
    return DummyMCP()


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["rag"])


class QueryRequest(BaseModel):
    """Request to query the RAG system."""
    question: str = Field(..., description="Question to ask the RAG")
    collection: str = Field(default="applications_1008", description="ChromaDB collection")
    chroma_path: str = Field(default="./chroma_db_1008", description="Path to ChromaDB")
    n_chunks: int = Field(default=5, ge=1, le=10, description="Number of chunks to retrieve")
    use_reranking: bool = Field(default=True, description="Whether to use reranking")
    timeout: int = Field(default=600, ge=10, le=1200, description="Timeout in seconds")


class ChunkInfo(BaseModel):
    id: str = Field(..., description="Chunk ID")
    similarity: float = Field(..., description="Similarity score")
    content: str = Field(default="", description="Chunk content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")


class QueryResponse(BaseModel):
    answer: str = Field(..., description="Generated answer")
    chunks: List[ChunkInfo] = Field(..., description="Source chunks used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Query metadata")


class CollectionInfo(BaseModel):
    name: str
    n_chunks: int
    embedding_model: str
    dimensions: int


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query_rag(request: QueryRequest) -> QueryResponse:
    try:
        logger.info(f"RAG query: {request.question[:50]}")
        mcp_client = await get_mcp_client()
        result = await mcp_client.query_rag(
            question=request.question,
            collection=request.collection,
            chroma_path=request.chroma_path,
            n_chunks=request.n_chunks,
            use_reranking=request.use_reranking,
            timeout=request.timeout,
        )
        chunks = [
            ChunkInfo(
                id=chunk.get("id", "unknown"),
                similarity=chunk.get("similarity", 0.0),
                content=chunk.get("content", ""),
                metadata=chunk.get("metadata", {}),
            )
            for chunk in result.get("chunks", [])
        ]
        return QueryResponse(
            answer=result.get("answer", "No answer"),
            chunks=chunks,
            metadata={
                "n_chunks": request.n_chunks,
                "use_reranking": request.use_reranking,
                "collection": request.collection,
            },
        )
    except Exception as e:
        logger.error(f"Query failed: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/collections", response_model=List[str], status_code=status.HTTP_200_OK)
async def list_collections(chroma_path: str = "./chroma_db_1008") -> List[str]:
    try:
        mcp_client = await get_mcp_client()
        return await mcp_client.list_collections(chroma_path=chroma_path)
    except Exception as e:
        logger.error(f"Failed to list collections: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/stats", response_model=CollectionInfo, status_code=status.HTTP_200_OK)
async def get_collection_stats(collection: str = "applications_1008", chroma_path: str = "./chroma_db_1008") -> CollectionInfo:
    try:
        mcp_client = await get_mcp_client()
        stats = await mcp_client.get_stats(collection=collection, chroma_path=chroma_path)
        return CollectionInfo(
            name=collection,
            n_chunks=stats.get("n_chunks", 0),
            embedding_model=stats.get("embedding_model", "unknown"),
            dimensions=stats.get("dimensions", 0),
        )
    except Exception as e:
        logger.error(f"Failed to get stats: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    return {"status": "ok", "service": "ambulon-webchat-rag"}


@router.get("/config", status_code=status.HTTP_200_OK)
async def get_config() -> Dict[str, Any]:
    import os
    return {
        "llm_provider": os.getenv("LLM_PROVIDER", "ollama"),
        "llm_model": os.getenv("LLM_MODEL", "llama3.2"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
    }
