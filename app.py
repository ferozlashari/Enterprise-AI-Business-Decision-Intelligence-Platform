"""
=========================================================
Hugging Face Gradio & FastAPI Bridge Entrypoint
=========================================================
"""

import gradio as gr
from backend.main import app as fastapi_app

# Define a simple interface to satisfy Hugging Face Space requirements
def platform_status():
    return "Enterprise AI Business Decision Intelligence Platform is active and running."

demo = gr.Interface(
    fn=platform_status,
    inputs=[],
    outputs="text",
    title="Enterprise AI Platform"
)

# Mount the existing FastAPI app from backend.main
app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=7860)
