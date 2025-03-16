import json
import os
from datasets import load_dataset
from evaluate import load as load_metric
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    pipeline,
)
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import requests
import zipfile
import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

# ✅ Use the direct link to the ZIP file from GitHub Assets
url = "https://github.com/Ved-Dixit/PIL/releases/download/ml/gpt2_pil_trained.zip"

# Download the ZIP file
response = requests.get(url)
zip_path = "gpt2_pil_trained.zip"

# Save the file
with open(zip_path, "wb") as f:
    f.write(response.content)

# Extract the ZIP file
with zipfile.ZipFile(zip_path, "r") as zip_ref:
    zip_ref.extractall("./model")
print("🚀 Loading GPT-2 model...")
gpt2_pil_generator = pipeline("text-generation", model='./model')


# 🎯 Improved GPT-2 generation with retries and stronger prompts
def generate_gpt_section(prompt, section_name=""):
    """Generate sections using GPT-2 with retries and better prompt control."""
    try:
        # First attempt at generation
        result = gpt2_pil_generator(
            prompt,
            max_length=512,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            num_return_sequences=1,
            do_sample=True,
            truncation=True,
        )
        generated_text = result[0]["generated_text"].replace(prompt, "").strip()

        # Retry with a stronger prompt if generation fails or gives junk
        if not generated_text or len(generated_text) < 20:
            print(f"⚠️ {section_name} generation failed — retrying with stronger prompt...")
            refined_prompt = (
                f"{prompt}\n\nEnsure the output is legally accurate, clear, and enforceable."
            )
            refined_result = gpt2_pil_generator(
                refined_prompt,
                max_length=512,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.2,
                num_return_sequences=1,
                do_sample=True,
                truncation=True,
            )
            generated_text = refined_result[0]["generated_text"].replace(refined_prompt, "").strip()

        # Final fallback if both attempts fail
        if not generated_text or len(generated_text) < 20:
            return f"⚠️ Unable to generate {section_name}. Please consult a legal expert."

        return generated_text

    except Exception as e:
        print(f"❌ Error generating {section_name}: {e}")
        return f"⚠️ Error generating {section_name}. Please check the input."


# 🛠️ Assemble the PIL Document with enhanced structure
def generate_pil(petitioner, respondent, subject, summary):
    """Create the full PIL document with powerful Legal Grounds, Prayer, and Court Procedure generation."""

    print("⚡ Generating Legal Grounds...")
    legal_grounds_prompt = (
        f"Draft strong, persuasive legal grounds for a Public Interest Litigation (PIL) on '{subject}', "
        f"citing specific constitutional articles, environmental laws (e.g., Environment Protection Act 1986), "
        f"legal principles (e.g., Precautionary Principle, Polluter Pays Principle), and landmark cases (e.g., M.C. Mehta v. Union of India 1987)."
        f"Ensure the argument is solid, legally backed, and supports the petitioner's cause."
    )
    legal_grounds = generate_gpt_section(legal_grounds_prompt, "Legal Grounds")

    print("⚡ Generating Prayer...")
    prayer_prompt = (
        f"Draft a clear, practical, and enforceable prayer (request) for a PIL on '{subject}', "
        f"including specific directives the court can issue (e.g., impose fines, enforce environmental audits, "
        f"order cleanup operations, penalize non-compliant industries, ensure public data transparency)."
    )
    prayer = generate_gpt_section(prayer_prompt, "Prayer")

    print("⚡ Generating Court Procedure...")
    court_procedure_prompt = (
        f"Draft a legally accurate and step-by-step court procedure for filing a Public Interest Litigation (PIL) "
        f"in the Supreme Court of India on '{subject}', ensuring it includes jurisdiction, notice, evidence submission, and requests for an expedited hearing."
    )
    court_procedure = generate_gpt_section(court_procedure_prompt, "Court Procedure")

    # ✅ Fallback version of Court Procedure in case GPT fails
    if "⚠️" in court_procedure:
        court_procedure = (
            "1. File the PIL under Article 32 of the Constitution for Supreme Court jurisdiction.\n"
            "2. Serve notice to the Respondent and the Attorney General of India.\n"
            "3. Attach supporting evidence such as scientific data, expert affidavits, and media reports.\n"
            "4. Request expedited hearing citing urgent public interest."
        )

    # ✅ Assemble the final PIL document
    pil_text = f"""
IN THE HON'BLE SUPREME COURT OF INDIA

PUBLIC INTEREST LITIGATION (PIL)

Petitioner: {petitioner}
Respondent: {respondent}

Subject: {subject}

Respected Lordships,

{summary}

Legal Grounds:
{legal_grounds}

Prayer:
{prayer}

Court Procedure:
{court_procedure}

Date: {datetime.now().strftime("%A, %d %B %Y")}

Yours sincerely,
{petitioner}
    """

    return pil_text


# 📄 Export PIL to TXT and PDF
def export_pil(pil_text, filename="PIL_Document"):
    """Export the PIL to text and PDF files."""
    # Save as TXT
    with open(f"{filename}.txt", "w", encoding="utf-8") as file:
        file.write(pil_text)
    print(f"✅ PIL saved as {filename}.txt")

    # Save as PDF
    pdf_file = f"{filename}.pdf"
    c = canvas.Canvas(pdf_file, pagesize=A4)
    c.setFont("Helvetica", 12)
    for i, line in enumerate(pil_text.split("\n")):
        c.drawString(40, 800 - (i * 20), line)
    c.save()
    print(f"✅ PIL saved as {pdf_file}")

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/run_pil_generator', methods=['POST'])
    # 🎯 Interactive CLI for PIL Generation
def run_pil_generator():
    data= request.json
    subject = data.get('subject')
    petitioner = data.get('petitioner')
    respondent = data.get('respondent')
    summary = data.get('summary')
    """Run the PIL Generator interactively."""
    print("🎉 Welcome to the PIL Generator!")


    # Generate the PIL document
    print("⚡ Generating the complete PIL document...")
    generated_pil = generate_pil(petitioner, respondent, subject, summary)
    return jsonify({'pil-text':generated_pil})
# 🔥 Run the Generator
if __name__ == "__main__":
    app.run()