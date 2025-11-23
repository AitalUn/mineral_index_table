from tqdm import tqdm
from docling.document_converter import DocumentConverter

source = papers_path  # document per local path or URL
converter = DocumentConverter()

papers_contents = {}

for paper_path in tqdm(papers_path.iterdir()):
    result = converter.convert(paper_path)  
    paper_contents = {
        "name": paper_path.name,
        "content": result.document.export_to_markdown()
    }
    # print(result.document.export_to_markdown())  # output: "## Docling Technical Report[...]
