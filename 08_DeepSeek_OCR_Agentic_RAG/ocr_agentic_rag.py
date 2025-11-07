import os
import asyncio
from pathlib import Path
from tempfile import gettempdir

from dotenv import load_dotenv
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import  (
    VlmPipelineOptions
)
from docling.datamodel.pipeline_options_vlm_model import (
    ApiVlmOptions, ResponseFormat
)
from docling.document_converter import (
    DocumentConverter, PdfFormatOption
)
from docling.pipeline.vlm_pipeline import VlmPipeline
import cognee
from cognee.infrastructure.databases.vector.embeddings.config import EmbeddingConfig

from common.utils.project_path import get_project_root, get_current_directory

load_dotenv(get_project_root() / ".env")

# I need to change the batch_size used by cognee for embedding through monkey patching.
def new_model_post_init(self, __context) -> None:
    if not self.embedding_batch_size and self.embedding_provider.lower() == "openai":
        self.embedding_batch_size = 2048
    elif not self.embedding_batch_size:
        self.embedding_batch_size = 64

EmbeddingConfig._original_model_post_init = EmbeddingConfig.model_post_init
EmbeddingConfig.model_post_init = new_model_post_init


class OCRAgenticRAG:
    def __init__(self,
                 api_key: str | None = None,
                 base_url: str | None = None,
                 temp_dir: str | Path | None = None):
        self.api_key = api_key or os.getenv("OCR_API_KEY")
        self.base_url = base_url or os.getenv("OCR_BASE_URL")
        self.temp_dir = temp_dir or gettempdir()
        self.converter = self._get_docling_converter(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    @staticmethod
    async def clear():
        await cognee.prune.prune_data()
        await cognee.prune.prune_system(metadata=True)

    async def add(self, files: str | list[str]):
        temp_files = self._ocr_pdf(files)
        print("All the PDF files have been successfully parsed.")

        await self.clear()
        await cognee.add(temp_files)
        await cognee.cognify()

    @staticmethod
    async def search(query: str) -> str:
        results = await cognee.search(
            query_text=query
        )
        return "\n".join([str(result) for result in results])


    def _ocr_pdf(self, source_data: str | list[str]) -> list[str]:
        if not isinstance(source_data, list):
            source_data = [source_data]

        output_files = []
        for source_file in source_data:
            result = self.converter.convert(source_file)
            markdown_str = result.document.export_to_markdown()
            source_filename = result.input.file.stem
            out_file = self._write_to_file(self.temp_dir, source_filename, markdown_str)
            output_files.append(out_file)

        return output_files

    @staticmethod
    def _write_to_file(output_dir: str | Path, filename: str, content: str) -> str:
        output_dir_path = Path(output_dir)
        if not output_dir_path.exists():
            output_dir_path.mkdir(parents=True, exist_ok=True)

        output_file = output_dir_path / Path(filename+".md")

        with open(output_file, "w", encoding="utf8") as f:
            f.write(content)
        return str(output_file.resolve())

    def _get_docling_converter(
            self,
            api_key: str = "",
            base_url: str = "",
    ) -> DocumentConverter:
        pipeline_options = VlmPipelineOptions(
            enable_remote_services=True
        )
        pipeline_options.vlm_options = self._openai_compatible_vlm_options(
            api_key=api_key,
            base_url=base_url
        )
        doc_converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                    pipeline_cls=VlmPipeline,
                )
            }
        )
        return doc_converter

    @staticmethod
    def _openai_compatible_vlm_options(
            model: str = "",
            prompt: str = "Convert these pdf pages to markdown.",
            response_format: ResponseFormat = ResponseFormat.MARKDOWN,
            base_url: str = "",
            temperature: float = 0.7,
            max_tokens: int = 4096,
            api_key: str = "",
            skip_special_token = False,
    ):
        ocr_model = model or os.getenv("OCR_MODEL")
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["Content-Type"] = "application/json"

        options = ApiVlmOptions(
            url=f"{base_url}/chat/completions",
            params=dict(
                model=ocr_model,
                max_tokens=max_tokens,
                skip_special_token=skip_special_token,
            ),
            headers=headers,
            prompt=prompt,
            timeout=90,
            scale=1.0,
            temperature=temperature,
            response_format=response_format,
        )
        return options


if __name__ == "__main__":
    ocr_rag = OCRAgenticRAG(temp_dir=get_current_directory()/"temp")
    async def main():
        source_dir = get_current_directory() / "temp"
        pdf_files = [
            source_dir / "NVIDIAAn.pdf"
        ]
        await ocr_rag.add(pdf_files)
        question = "How much was Nvidia’s revenue in Q2 Fiscal 2025?"
        result = await ocr_rag.search(query=question)

        print("\n\n\n--------------------\n")
        print(f"Question: >>> {question}")
        print(f"Search Result: >>> {result}")

    asyncio.run(main())
