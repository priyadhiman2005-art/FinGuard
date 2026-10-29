"""
FinGuard - Report & Presentation Chart Generator
Generates clean, authentic high-resolution chart assets using Pillow.
"""

import os
from PIL import Image, ImageDraw, ImageFont

CHARTS_DIR = os.path.dirname(__file__)


def get_font(size: int, bold: bool = False):
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except Exception:
        return ImageFont.load_default()


def generate_confusion_matrix_chart():
    img = Image.new("RGB", (900, 360), color="#1E222D")
    draw = ImageDraw.Draw(img)

    f_title = get_font(20, bold=True)
    f_header = get_font(15, bold=True)
    f_sub = get_font(12, bold=False)
    f_val = get_font(18, bold=True)

    draw.text((20, 15), "Held-Out Test Set Confusion Matrix Comparison (N = 1,364, Defaults = 44)", fill="#FFFFFF", font=f_title)

    # Matrix 1: Baseline Logistic Regression
    draw.text((80, 55), "Baseline: Logistic Regression", fill="#3498DB", font=f_header)
    draw.text((80, 75), "class_weight='balanced' (Threshold = 0.50)", fill="#9AA0A6", font=f_sub)

    # TN: 577, FP: 743, FN: 11, TP: 33
    draw.rectangle([60, 105, 200, 180], fill="#2C3E50", outline="#34495E", width=2)
    draw.text((85, 120), "TN: 577", fill="#ECF0F1", font=f_val)
    draw.text((75, 148), "Correct Solvent", fill="#BDC3C7", font=f_sub)

    draw.rectangle([210, 105, 350, 180], fill="#C0392B", outline="#E74C3C", width=2)
    draw.text((235, 120), "FP: 743", fill="#FFFFFF", font=f_val)
    draw.text((225, 148), "False Alarms!", fill="#FFD2D2", font=f_sub)

    draw.rectangle([60, 190, 200, 265], fill="#E67E22", outline="#D35400", width=2)
    draw.text((85, 205), "FN: 11", fill="#FFFFFF", font=f_val)
    draw.text((75, 233), "Missed Default", fill="#FFEAA7", font=f_sub)

    draw.rectangle([210, 190, 350, 265], fill="#27AE60", outline="#2ECC71", width=2)
    draw.text((235, 205), "TP: 33", fill="#FFFFFF", font=f_val)
    draw.text((225, 233), "Caught Default", fill="#D4EFDF", font=f_sub)

    draw.text((60, 280), "Recall: 75.0% | Precision: 4.25% | FPs: 743", fill="#E74C3C", font=f_header)
    draw.text((60, 305), "Asymmetric Loss (FP + 20*FN): 963.0 units", fill="#BDC3C7", font=f_sub)

    # Matrix 2: Improved Random Forest
    draw.text((540, 55), "Improved: Random Forest", fill="#2ECC71", font=f_header)
    draw.text((540, 75), "Balanced Ensemble 150 Trees (Threshold = 0.50)", fill="#9AA0A6", font=f_sub)

    # TN: 1290, FP: 30, FN: 22, TP: 22
    draw.rectangle([520, 105, 660, 180], fill="#27AE60", outline="#2ECC71", width=2)
    draw.text((540, 120), "TN: 1,290", fill="#FFFFFF", font=f_val)
    draw.text((535, 148), "Correct Solvent", fill="#D4EFDF", font=f_sub)

    draw.rectangle([670, 105, 810, 180], fill="#2C3E50", outline="#34495E", width=2)
    draw.text((700, 120), "FP: 30", fill="#ECF0F1", font=f_val)
    draw.text((690, 148), "96% Fewer FPs!", fill="#2ECC71", font=f_sub)

    draw.rectangle([520, 190, 660, 265], fill="#E67E22", outline="#D35400", width=2)
    draw.text((550, 205), "FN: 22", fill="#FFFFFF", font=f_val)
    draw.text((535, 233), "Missed Default", fill="#FFEAA7", font=f_sub)

    draw.rectangle([670, 190, 810, 265], fill="#2980B9", outline="#3498DB", width=2)
    draw.text((700, 205), "TP: 22", fill="#FFFFFF", font=f_val)
    draw.text((690, 233), "Caught Default", fill="#AED6F1", font=f_sub)

    draw.text((520, 280), "ROC-AUC: 0.9466 | PR-AUC: 0.4610", fill="#2ECC71", font=f_header)
    draw.text((520, 305), "Asymmetric Loss: 470.0 units (51.2% Reduction)", fill="#BDC3C7", font=f_sub)

    out_path = os.path.join(CHARTS_DIR, "chart_confusion_matrix.png")
    img.save(out_path, dpi=(150, 150))
    print(f"Generated {out_path}")


def generate_feature_importance_chart():
    img = Image.new("RGB", (900, 380), color="#1E222D")
    draw = ImageDraw.Draw(img)

    f_title = get_font(20, bold=True)
    f_sub = get_font(13, bold=False)
    f_item = get_font(12, bold=False)
    f_bar = get_font(11, bold=True)

    draw.text((20, 15), "Top Empirical Risk Drivers — Random Forest Feature Importance (MDI)", fill="#FFFFFF", font=f_title)
    draw.text((20, 42), "Empirical feature attributions on 95 corporate financial ratios (UCI Taiwan Benchmark)", fill="#9AA0A6", font=f_sub)

    features = [
        ("Borrowing dependency", 0.05693),
        ("Net Income to Total Assets", 0.04894),
        ("Persistent EPS in the Last Four Seasons", 0.04667),
        ("Total debt / Total net worth", 0.03929),
        ("Net worth / Assets", 0.03434),
        ("Equity to Liability", 0.03419),
        ("Liability to Equity", 0.02994),
        ("Total income / Total expense", 0.02958),
        ("Continuous interest rate (after tax)", 0.02907),
        ("Retained Earnings to Total Assets", 0.02729),
    ]

    max_val = 0.06
    bar_x_start = 320
    max_bar_width = 480
    y_start = 75
    row_height = 28

    for i, (name, val) in enumerate(features):
        y = y_start + i * row_height
        draw.text((30, y + 4), f"{i+1}. {name}", fill="#ECF0F1", font=f_item)
        bar_len = int((val / max_val) * max_bar_width)
        # Gradient tone
        fill_color = "#1ABC9C" if i < 3 else "#3498DB"
        draw.rectangle([bar_x_start, y + 2, bar_x_start + bar_len, y + 20], fill=fill_color)
        draw.text((bar_x_start + bar_len + 10, y + 4), f"{val*100:.2f}%", fill="#FFFFFF", font=f_bar)

    out_path = os.path.join(CHARTS_DIR, "chart_feature_importance.png")
    img.save(out_path, dpi=(150, 150))
    print(f"Generated {out_path}")


def generate_indian_cases_chart():
    img = Image.new("RGB", (900, 390), color="#1E222D")
    draw = ImageDraw.Draw(img)

    f_title = get_font(20, bold=True)
    f_sub = get_font(13, bold=False)
    f_item = get_font(12, bold=False)
    f_bar = get_font(11, bold=True)

    draw.text((20, 15), "Indian Corporate Distress Benchmark: Pre-Event Altman Z-Score", fill="#FFFFFF", font=f_title)
    draw.text((20, 42), "All 10 distressed Indian entities detected in the Distress Zone prior to official insolvency/RBI takeover", fill="#9AA0A6", font=f_sub)

    cases = [
        ("Dewan Housing Finance (DHFL)", 1.099, "Non-Mfg (Cutoff 1.10)"),
        ("Jet Airways (India) Ltd", -6.639, "Non-Mfg (Cutoff 1.10)"),
        ("Reliance Communications (RCom)", -1.221, "Non-Mfg (Cutoff 1.10)"),
        ("Sintex Industries Ltd", -0.437, "Mfg (Cutoff 1.81)"),
        ("Bhushan Steel Ltd", 0.160, "Mfg (Cutoff 1.81)"),
        ("Cox & Kings Ltd", -0.493, "Non-Mfg (Cutoff 1.10)"),
        ("Amtek Auto Ltd", 0.266, "Mfg (Cutoff 1.81)"),
        ("Videocon Industries Ltd", -0.387, "Mfg (Cutoff 1.81)"),
        ("IL&FS Ltd", 0.102, "Non-Mfg (Cutoff 1.10)"),
        ("ABG Shipyard Ltd", -0.775, "Mfg (Cutoff 1.81)"),
    ]

    y_start = 75
    row_height = 29
    zero_x = 420  # Position of Z=0 line
    scale = 35.0  # Pixels per unit Z

    # Draw Zero axis line
    draw.line([zero_x, 70, zero_x, 370], fill="#7F8C8D", width=2)
    draw.text((zero_x - 10, 55), "Z = 0", fill="#BDC3C7", font=f_bar)

    # Distress cutoff line (Z = 1.81)
    distress_x = int(zero_x + 1.81 * scale)
    draw.line([distress_x, 70, distress_x, 370], fill="#E74C3C", width=1)
    draw.text((distress_x - 30, 55), "Cutoff 1.81", fill="#E74C3C", font=f_bar)

    for i, (name, z, note) in enumerate(cases):
        y = y_start + i * row_height
        draw.text((25, y + 4), f"{name}", fill="#ECF0F1", font=f_item)
        
        # Draw bar from zero_x
        bar_x = int(zero_x + z * scale)
        if z < 0:
            draw.rectangle([max(bar_x, 230), y + 3, zero_x, y + 21], fill="#E74C3C")
            draw.text((max(bar_x, 230) - 50, y + 4), f"{z:.2f}", fill="#FF7675", font=f_bar)
        else:
            draw.rectangle([zero_x, y + 3, bar_x, y + 21], fill="#F39C12")
            draw.text((bar_x + 8, y + 4), f"{z:.2f}", fill="#FDCB6E", font=f_bar)

        draw.text((630, y + 4), f"Distress Zone | {note}", fill="#E74C3C" if z < 0.5 else "#F39C12", font=f_bar)

    out_path = os.path.join(CHARTS_DIR, "chart_indian_cases.png")
    img.save(out_path, dpi=(150, 150))
    print(f"Generated {out_path}")


if __name__ == "__main__":
    generate_confusion_matrix_chart()
    generate_feature_importance_chart()
    generate_indian_cases_chart()

