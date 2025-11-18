from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
import tempfile
import io
from docx2pdf import convert
import os
import asyncio

app = FastAPI(title="DOCX to PDF API")

async def remove_file(path: str):
    try:
        await asyncio.sleep(0.5)
        os.remove(path)
    except Exception:
        pass

@app.post("/convert-to-pdf")
async def convert_to_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    
    tmp_docx = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    tmp_docx.write(await file.read())
    tmp_docx.close()

    
    tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp_pdf.close()
    convert(tmp_docx.name, tmp_pdf.name)

    
    pdf_bytes = io.BytesIO(open(tmp_pdf.name, "rb").read())

    
    background_tasks.add_task(remove_file, tmp_docx.name)
    background_tasks.add_task(remove_file, tmp_pdf.name)

    
    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={file.filename.split('.')[0]}.pdf"}
    )