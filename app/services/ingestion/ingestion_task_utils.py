import re
import uuid
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct
from typing import Tuple, List, Dict
from langchain_openai import OpenAIEmbeddings
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption
from docling.document_converter import DocumentConverter
from docling_core.types.doc.document import DoclingDocument
from docling.datamodel.pipeline_options import PdfPipelineOptions

from app.core.settings import settings

qdrant_client = QdrantClient(url=settings.qdrant_url, timeout=5)
embeddings = OpenAIEmbeddings(
    model=settings.model_id,
    api_key=settings.openai_api_key
)

async def prep_embedings(documents: List[Dict])->List[List[float]]:
    return await embeddings.aembed_documents([doc["text"] for doc in documents])

def deterministic_chunk_id(metadata: dict, index_name: str) -> str:
    metadata_str = (
        f"{metadata.get('file_name','')}"
        f"{metadata.get('page_no','')}"
        f"{index_name}"
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, metadata_str))

def parse_pdf(path: str)->DoclingDocument:
    pipeline_options = PdfPipelineOptions(
        generate_picture_images=True,
    )
    converter = DocumentConverter(
        format_options={ InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options) }
    )
    conv_res = converter.convert(path)
    doc = conv_res.document
    return doc

def to_markdown_page_wise(doc: DoclingDocument, page_no: int)-> Tuple[str, List[str]]:
    text = doc.export_to_markdown(page_no=page_no,
                                  image_mode="embedded")
    pattern = r'!\[[^\]]*\]\([^\)]*'
    images = re.findall(pattern, text)
    clean_md = re.sub(pattern, '', text)
    return clean_md, images

def prep_docs_page_wise(doc: DoclingDocument)-> List[Dict]:
    documents = []
    base_document = doc.origin.model_dump()
    for page_number, __ in doc.pages.items():
        document = {}
        document["metadata"] = {"mimetype": base_document.get("mimetype", "N/A"),
                                "file_name": base_document.get("filename", "N/A"),
                                "page_no": page_number}
        clean_md, __ = to_markdown_page_wise(doc, page_number)
        document["text"] = clean_md
        documents.append(document)
    return documents

def ingest_docs(documents: List[Dict],
                embeddings_list: List[float],
                index_name: str,
                batch_size: int = 64
                ):
    points = []
    for i in range(len(documents)):
        doc = documents[i]
        points.append(
            PointStruct(
                id=deterministic_chunk_id(doc.get("metadata", {}), index_name),
                vector={
                    "dense": embeddings_list[i],
                    "bm25": models.Document(
                        text=doc["text"],
                        model="Qdrant/bm25",
                    )
                },
                payload=doc
            )
        )
        # If batch is full or end is reached, upsert and clear
        if len(points) >= batch_size or i == len(documents) - 1:
            print(f"Starting ingestion of {len(points)} points...")
            qdrant_client.upsert(
                collection_name=index_name,
                points=points,
                wait=True
            )
            points = []