"""
Gradio interface for the Campus Dining Unofficial Guide.

Run:  python app.py
Then open: http://localhost:7860
"""

import gradio as gr

from query import ask


def handle_query(question: str):
    """Bridge between the Gradio UI and the ask() pipeline."""
    if not question.strip():
        return "", ""
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="Campus Dining Unofficial Guide") as demo:
    gr.Markdown(
        "## Campus Dining Unofficial Guide\n"
        "Ask questions about student dining experiences across US universities. "
        "Answers are grounded in student newspaper reviews, Yelp ratings, and campus blogs."
    )

    inp = gr.Textbox(
        label="Your question",
        placeholder=(
            'e.g. "What do Cornell students think about Okenshields?" '
            'or "What are Harvard students saying about HUDS menu changes?"'
        ),
        lines=2,
    )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer_box = gr.Textbox(label="Answer", lines=8, show_copy_button=True)
        sources_box = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer_box, sources_box])
    inp.submit(handle_query, inputs=inp, outputs=[answer_box, sources_box])

if __name__ == "__main__":
    demo.launch()
