from fpdf import FPDF

from ..schema import Worksheet


def worksheet_to_pdf(ws: Worksheet, output_path: str) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, ws.title, ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Age: {ws.age}   Destination: {ws.destination}", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Fun Facts", ln=True)
    pdf.set_font("Arial", size=12)
    for i, fact in enumerate(ws.fun_facts, 1):
        pdf.multi_cell(0, 6, f"{i}. {fact}")

    pdf.ln(4)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "Quiz", ln=True)
    pdf.set_font("Arial", size=12)
    for i, item in enumerate(ws.quiz, 1):
        pdf.multi_cell(0, 6, f"{i}. {item.q}")
        for j, opt in enumerate(item.a):
            pdf.multi_cell(0, 6, f"  ({j}) {opt}")
        pdf.ln(2)

    pdf.output(output_path)
