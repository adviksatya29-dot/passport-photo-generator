from flask import Flask, render_template, request
from rembg import remove
from PIL import (
    Image,
    ImageEnhance,
    ImageFilter
)
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    'static',
    'uploads'
)

OUTPUT_FOLDER = os.path.join(
    BASE_DIR,
    'static',
    'output'
)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():

    file = request.files['photo']

    copies = int(request.form['copies'])

    bg_color = request.form['bg_color']

    if file:

        # Save uploaded image
        input_path = os.path.join(
            app.config['UPLOAD_FOLDER'],
            file.filename
        )

        file.save(input_path)

        # Open image
        input_image = Image.open(input_path).convert("RGBA")

        # Remove background
        removed_bg = remove(input_image)

        # Background colors
        if bg_color == "blue":
            bg = (67, 104, 173)

        elif bg_color == "white":
            bg = (255, 255, 255)

        elif bg_color == "red":
            bg = (220, 20, 60)

        else:
            bg = (255, 255, 255)

        # Create passport background
        background = Image.new(
            "RGB",
            removed_bg.size,
            bg
        )

        # Paste person
        background.paste(
            removed_bg,
            mask=removed_bg.split()[3]
        )

        output_image = background

        # Professional passport size
        passport_size = (390, 500)

        # HD resize
        output_image = output_image.resize(
            passport_size,
            Image.LANCZOS
        )

        # Enhance quality
        sharpness = ImageEnhance.Sharpness(
            output_image
        )

        output_image = sharpness.enhance(2.5)

        contrast = ImageEnhance.Contrast(
            output_image
        )

        output_image = contrast.enhance(1.2)

        output_image = output_image.filter(
            ImageFilter.SHARPEN
        )

        # Real 4x6 glossy paper
        paper_width = 1200
        paper_height = 1800

        # White glossy sheet
        sheet = Image.new(
            'RGB',
            (paper_width, paper_height),
            'white'
        )

        # Professional layout
        margin_x = 90
        margin_y = 90

        gap_x = 50
        gap_y = 50

        cols = 2

        for i in range(copies):

            row = i // cols
            col = i % cols

            x = margin_x + col * (
                passport_size[0] + gap_x
            )

            y = margin_y + row * (
                passport_size[1] + gap_y
            )

            # Prevent overflow
            if y + passport_size[1] > paper_height:
                break

            sheet.paste(output_image, (x, y))

        # Save output
        output_filename = "passport_sheet.png"

        output_path = os.path.join(
            app.config['OUTPUT_FOLDER'],
            output_filename
        )

        sheet.save(
            output_path,
            dpi=(300, 300),
            optimize=True
        )

        return render_template(
            'result.html',
            image=f'output/{output_filename}'
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
