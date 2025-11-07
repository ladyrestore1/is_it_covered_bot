from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import openai

app = FastAPI()
openai.api_key = "YOUR_OPENAI_API_KEY"   # use env var later!

HTML_PAGE = """
<html><body style='font-family:Inter;max-width:600px;margin:auto'>
<h2>Is It Covered? 🧾</h2>
<form method='post'>
<textarea name='question' rows='4' style='width:100%' placeholder='Describe your damage...'></textarea><br>
<button type='submit'>Check Coverage</button>
</form>
<p>{response}</p>
<p style='font-size:12px;color:gray'>Disclaimer: Educational only, not legal advice.</p>
</body></html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_PAGE.format(response="")

@app.post("/", response_class=HTMLResponse)
async def ask(request: Request):
    form = await request.form()
    q = form["question"]
    answer = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role":"system","content":
             "You are Lady Restore, a restoration claims helper. "
             "Explain likely coverage in plain, educational terms."},
            {"role":"user","content":q}
        ],
        max_tokens=300
    )
    reply = answer.choices[0].message.content
    return HTML_PAGE.format(response=reply)
