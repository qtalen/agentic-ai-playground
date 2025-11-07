from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    RapidOcrOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption

from common.utils.project_path import get_current_directory


def main():
    pdf_file = get_current_directory() / "temp/NVIDIAAn.pdf"

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    ocr_options = RapidOcrOptions(
        force_full_page_ocr=False,
    )
    pipeline_options.ocr_options = ocr_options

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }
    )

    doc = converter.convert(pdf_file).document
    md = doc.export_to_markdown()

    with open(get_current_directory() / "temp/NVIDIAAn_rapid.md", "w", encoding="utf8") as f:
        f.write(md)


if __name__ == "__main__":
    main()
