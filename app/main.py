# from fastapi import FastAPI, UploadFile, File, BackgroundTasks
# from fastapi.responses import StreamingResponse
# import tempfile
# import io
# from docx2pdf import convert
# import os
# import asyncio

# app = FastAPI(title="DOCX to PDF API")

# async def remove_file(path: str):
#     try:
#         await asyncio.sleep(0.5)
#         os.remove(path)
#     except Exception:
#         pass

# @app.post("/convert-to-pdf")
# async def convert_to_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    
#     tmp_docx = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
#     tmp_docx.write(await file.read())
#     tmp_docx.close()

    
#     tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
#     tmp_pdf.close()
#     convert(tmp_docx.name, tmp_pdf.name)

    
#     pdf_bytes = io.BytesIO(open(tmp_pdf.name, "rb").read())

    
#     background_tasks.add_task(remove_file, tmp_docx.name)
#     background_tasks.add_task(remove_file, tmp_pdf.name)

    
#     return StreamingResponse(
#         pdf_bytes,
#         media_type="application/pdf",
#         headers={"Content-Disposition": f"attachment; filename={file.filename.split('.')[0]}.pdf"}
#     )

import os
import tempfile
import subprocess
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi import BackgroundTasks

app = FastAPI()

@app.post("/convert-to-pdf")
async def convert_to_pdf(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="File harus .docx")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_docx:
        tmp_docx.write(await file.read())
        tmp_docx_path = tmp_docx.name

    tmp_pdf_path = tmp_docx_path.replace(".docx", ".pdf")

    try:
        subprocess.run([
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", os.path.dirname(tmp_docx_path),
            tmp_docx_path
        ], check=True)

        if not os.path.exists(tmp_pdf_path):
            raise HTTPException(status_code=500, detail="Gagal membuat PDF")

        # Tambahkan background job untuk hapus file
        background_tasks.add_task(cleanup_files, [tmp_docx_path, tmp_pdf_path])

        return FileResponse(
            tmp_pdf_path,
            media_type="application/pdf",
            filename="converted.pdf",
            background=background_tasks
        )

    except Exception as e:
        cleanup_files([tmp_docx_path])
        raise HTTPException(status_code=500, detail=str(e))

def cleanup_files(paths):
    for path in paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except:
            pass
