import os
from PIL import Image, ImageDraw, ImageFont

def generate_icons():
    os.makedirs("assets", exist_ok=True)
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background rounded container with modern gradient feel
    # Deep slate/blue background #0f172a
    draw.rounded_rectangle([8, 8, 248, 248], radius=50, fill="#0f172a")

    # Vibrant accent border (Foursys cyan/teal #06b6d4)
    draw.rounded_rectangle([10, 10, 246, 246], radius=48, outline="#06b6d4", width=6)

    # Inner decorative glow circle
    draw.ellipse([50, 40, 206, 196], outline="#1e293b", width=4)

    # Draw a stylized modern Key
    # Key head (circle)
    draw.ellipse([70, 75, 140, 145], outline="#38bdf8", width=12, fill="#0f172a")
    draw.ellipse([92, 97, 118, 123], fill="#38bdf8")

    # Key shaft
    draw.rounded_rectangle([130, 102, 195, 118], radius=6, fill="#38bdf8")

    # Key teeth
    draw.rounded_rectangle([165, 116, 177, 142], radius=4, fill="#38bdf8")
    draw.rounded_rectangle([183, 116, 195, 134], radius=4, fill="#38bdf8")

    # Modern "M" badge in lower right corner (Bradesco Chave M homage)
    # Circle badge with Red-Orange / Coral #ef4444 or #dc2626
    draw.ellipse([145, 145, 235, 235], fill="#dc2626", outline="#ffffff", width=4)
    
    # Draw "M" inside the badge
    # M points:
    m_color = "#ffffff"
    # Left bar
    draw.rounded_rectangle([165, 168, 175, 214], radius=3, fill=m_color)
    # Right bar
    draw.rounded_rectangle([205, 168, 215, 214], radius=3, fill=m_color)
    # Diagonal left to center
    draw.polygon([(170, 168), (177, 168), (192, 195), (188, 195)], fill=m_color)
    # Diagonal right to center
    draw.polygon([(210, 168), (203, 168), (188, 195), (192, 195)], fill=m_color)

    png_path = os.path.join("assets", "icon.png")
    img.save(png_path, "PNG")
    print(f"Generated {png_path}")

    # Generate ICO with multiple sizes for Windows
    ico_path = os.path.join("assets", "icon.ico")
    img.save(ico_path, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Generated {ico_path}")

if __name__ == "__main__":
    generate_icons()
