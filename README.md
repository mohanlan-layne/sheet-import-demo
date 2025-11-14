# sheet-import-demo

Sheet import API demo built with FastAPI. It exposes an upload endpoint that validates incoming files and stores them temporarily for later processing.

## Requirements

- Python 3.11+
- Packages listed in `requirements.txt`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Upload endpoint

- URL: `POST /uploads/`
- Header requirements:
  - `Content-Type: multipart/form-data`
  - `X-Upload-Token: <token>`
- Form field: `file`
- Supported MIME types: `text/csv`, `application/vnd.ms-excel`, `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- Maximum file size: 5 MiB

On success the API responds with a JSON payload containing a temporary file identifier and metadata about the uploaded file.
