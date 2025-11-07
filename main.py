from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from openai import OpenAI
import os

app = FastAPI()

# Uses the OPENAI_API_KEY environment variable from Render
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Is It Covered? - Lady Restore</title>
    <style>
        body {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background-color: #0b0b10;
            color: #f9fafb;
            display: flex;
            justify-content: center;
            padding: 40px 16px;
        }}
        .card {{
            background: #111827;
            border-radius: 16px;
            padding: 24px 20px;
            max-width: 640px;
            width: 100%;
            box-shadow: 0 18px 45px rgba(0,0,0,0.55);
            border: 1px solid #1f2937;
        }}
        h1 {{
            font-size: 1.8rem;
            margin-bottom: 4px;
            color: #e5e7eb;
        }}
        h2 {{
            font-size: 0.95rem;
            margin-top: 0;
            margin-bottom: 16px;
            color: #9ca3af;
            font-weight: 400;
        }}
        textarea {{
            width: 100%;
            min-height: 120px;
            border-radius: 10px;
            border: 1px solid #374151;
            background: #020617;
            color: #f9fafb;
            padding: 10px 12px;
            resize: vertical;
            font-size: 0.95rem;
        }}
        textarea:focus {{
            outline: none;
            border-color: #38bdf8;
            box-shadow: 0 0 0 1px #38bdf8;
        }}
        button {{
            margin-top: 12px;
            background: linear-gradient(90deg, #6366f1, #22c55e);
            border: none;
            color: white;
            padding: 10px 18px;
            border-radius: 999px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
        }}
        button:hover {{
            filter: brightness(1.05);
        }}
        .response {{
            margin-top: 18px;
            padding-top: 14px;
            border-top: 1px solid #1f2937;
            font-size: 0.95rem;
            line-height: 1.5;
            color: #e5e7eb;
        }}
        .badge {{
            display: inline-block;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            background: #1f2937;
            color: #a5b4fc;
            padding: 4px 10px;
            border-radius: 999px;
            margin-bottom: 8px;
        }}
        .disclaimer {{
            margin-top: 12px;
            font-size: 0.7rem;
            color: #9ca3af;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="badge">Lady Restore · Claim Helper</div>
        <h1>Is It Covered?</h1>
        <h2>Describe what happened, how the damage occurred, and anything your insurance company has told you so far.</h2>
        <form method="post">
            <textarea name="question" placeholder="Example: A pipe burst in my upstairs bathroom and water leaked into the kitchen below..."></textarea>
            <button type="submit">Check Coverage</button>
        </form>
        <div class="response">
            {response_html}
        </div>
        <div class="disclaimer">
            This tool is for educational purposes only and does not replace legal, insurance, or professional advice.
        </div>
    </div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_form():
    return HTML_TEMPLATE.format(response_html="")

@app.post("/", response_class=HTMLResponse)
def handle_form(question: str = Form(...)):
    if not question.strip():
        return HTML_TEMPLATE.format(response_html="Please describe your damage so I can help interpret possible coverage.")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are Lady Restore, a restoration and insurance claims helper. "
                    "You help homeowners understand possible insurance coverage for property damage. "
                    "You are NOT their carrier, adjuster, attorney, or public adjuster. "
                    "You explain likely coverage scenarios, key policy issues, and suggested questions "
                    "they should ask their insurance company or contractor, in plain language. "
                    "Always include:\n"
                    "- a simple summary (Likely covered / Possibly covered / Unlikely covered)\n"
                    "- the reasoning\n"
                    "- 2–4 next steps they can take.\n"
                    "Stay educational, neutral, and clear. Do not guarantee outcomes."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        max_tokens=500,
        temperature=0.25,
    )

    answer = completion.choices[0].message.content
    # Convert newlines to <br> for HTML
    safe_answer = answer.replace("\n", "<br>")
    return HTML_TEMPLATE.format(response_html=safe_answer)


