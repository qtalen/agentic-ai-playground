This code repo has the source code for my article [How To Use DeepSeek-OCR And Docling For PDF Parsing](https://www.dataleadsfuture.com/how-to-use-deepseek-ocr-and-docling-for-pdf-parsing/).

To run this project, you should first install it along with its needed dependencies.

```shell
cd ..
pip install --upgrade -e .
```

Next, just like in the article, add the `API KEY` and `BASE URL` for DeepSeek-OCR, LLM, and the Embedding model into the `.env` file.

This project has only two files:

1. `ocr_agentic_rag.py`: shows how to use DeepSeek-OCR together with docling to parse PDF files.
2. `paddle_ocr_docling.py`: used as a comparison to check how well DeepSeek-OCR actually parses.

I used [NVIDIA’s FY2026 Q2 financial report](https://nvidianews.nvidia.com/_gallery/download_pdf/68af69043d6332f1d02dec91/?ref=dataleadsfuture.com) as sample data. You should create a `temp` folder under `08_DeepSeek_OCR_Agentic_RAG`, then put the downloaded `NVIDIAAn.pdf` file into that `temp` folder.