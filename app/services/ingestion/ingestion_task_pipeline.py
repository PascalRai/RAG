import asyncio
from app.services.ingestion.ingestion_task_utils import (
    parse_pdf,
    prep_embedings,
    prep_docs_page_wise,
    ingest_docs,
)

def ingestion_pipeline(
        filename: str,
        index_name: str
        ):
    print(f"parsing file: {filename}")
    doc = parse_pdf(filename)
    documents = prep_docs_page_wise(doc)
    print(f"Creating embeddings for {len(documents)} docs")
    embedding_list = asyncio.run(prep_embedings(documents))
    ingest_docs(documents,
                embedding_list,
                index_name
                )
    return True

if __name__=="__main__":
    from glob import glob

    for path in glob("dev/v1/docs/*.pdf"):
        if path == "dev/v1/docs/2022 Q3 AAPL.pdf":
            continue
        ingestion_pipeline(
            filename=path,
            index_name="test_hybrid"
        )