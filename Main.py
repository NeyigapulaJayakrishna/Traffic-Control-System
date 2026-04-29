from tkinter import *
import tkinter
from tkinter import filedialog, messagebox
import numpy as np
from CannyEdgeDetector import *
import matplotlib.image as mpimg
import cv2
from PIL import Image, ImageTk
import os

# ---------------- MAIN WINDOW ----------------
main = tkinter.Tk()
main.title("Density Based Smart Traffic Control System")
main.geometry("1300x700")
main.configure(bg="white")

# ---------------- GLOBALS ----------------
filename = ""
refrence_pixels = 0
sample_pixels = 0

# ---------------- PROFESSIONAL COLORS (BLUE THEME) ----------------
TOP_BG = "#4BAAFC"           # light blue top bar
TOP_FG = "#FFFFFF"          # dark blue text
BORDER_CLR = "#4BAAFC"      # light blue border

LEFT_BG = "#4BAAFC"
RIGHT_BG = "#FFFFFF"

BTN_BG = "#DCDDE1"
BTN_FG = "#111827"
BTN_ACTIVE = "#1D4ED8"

EXIT_BG = "#C84646"
EXIT_FG = "#FFFFFF"
EXIT_ACTIVE = "#FECACA"

TEXT_FG = "#FFFFFF"
SUBTEXT_FG = "#25796D"


# ---------------- FUNCTIONS ----------------

def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


# ✅ show image in label (normal output size)
def show_image_in_label(img_path, target_label, w=320, h=420):
    try:
        img = Image.open(img_path)
        img = img.resize((w, h))
        img_tk = ImageTk.PhotoImage(img)

        target_label.config(image=img_tk)
        target_label.image = img_tk
    except:
        output_text.config(text="❌ Image not found / cannot display.")


# ✅ full background image (only at start)
def show_full_background(img_path):
    try:
        img = Image.open(img_path)
        img = img.resize((900, 600))
        img_tk = ImageTk.PhotoImage(img)

        image_label1.config(image=img_tk)
        image_label1.image = img_tk

        image_label2.config(image="")  # clear 2nd label at start
        image_label2.image = None
    except:
        pass


# Hide output at start
def hide_output_ui():
    output_title.pack_forget()
    output_text.pack_forget()

def show_output_ui():
    output_title.pack(pady=(10, 5))
    output_text.pack(pady=(5, 10))


def uploadTrafficImage():
    global filename

    filename = filedialog.askopenfilename(
        initialdir="images",
        filetypes=[("Image Files", "*.png *.jpg *.jpeg")]
    )

    if filename:
        show_output_ui()
        pathlabel.config(text=filename)
        output_text.config(text="✅ Traffic image uploaded successfully!")

        # ✅ Show uploaded image in LEFT image area
        show_image_in_label(filename, image_label1)

        # clear 2nd image until canny applied
        image_label2.config(image="")
        image_label2.image = None


def applyCanny():
    global filename

    if filename == "":
        messagebox.showerror("Error", "Please upload traffic image first!")
        return

    show_output_ui()

    imgs = []
    img = mpimg.imread(filename)
    img = rgb2gray(img)
    imgs.append(img)

    edge = CannyEdgeDetector(
        imgs,
        sigma=1.4,
        kernel_size=5,
        lowthreshold=0.09,
        highthreshold=0.20,
        weak_pixel=100
    )

    imgs = edge.detect()

    for i, img in enumerate(imgs):
        if img.shape[0] == 3:
            img = img.transpose(1, 2, 0)

    if not os.path.exists("gray"):
        os.mkdir("gray")

    cv2.imwrite("gray/test.png", img)

    output_text.config(text="Canny Edge Detection applied successfully!")

    # ✅ Show 2 images:
    # 1) original uploaded
    show_image_in_label(filename, image_label1)

    # 2) canny output
    show_image_in_label("gray/test.png", image_label2)


def pixelcount():
    global refrence_pixels
    global sample_pixels

    try:
        show_output_ui()

        img = cv2.imread("gray/test.png", cv2.IMREAD_GRAYSCALE)
        sample_pixels = np.sum(img == 255)

        img = cv2.imread("gray/refrence.png", cv2.IMREAD_GRAYSCALE)
        refrence_pixels = np.sum(img == 255)

        output_text.config(
            text=f"📌 Pixel Count Completed!\n\n"
                 f"Sample White Pixels : {sample_pixels}\n"
                 f"Reference White Pixels : {refrence_pixels}"
        )
    except:
        messagebox.showerror(
            "Error",
            "Please apply canny preprocessing first!\nAlso make sure gray/refrence.png exists."
        )


def timeAllocation():
    global refrence_pixels
    global sample_pixels

    if refrence_pixels == 0:
        messagebox.showerror("Error", "First calculate pixel count!")
        return

    show_output_ui()

    avg = (sample_pixels / refrence_pixels) * 100

    if avg >= 90:
        msg = "🚦 Traffic is VERY HIGH\nGreen Signal Time : 60 secs"
    elif avg > 85 and avg < 90:
        msg = "🚦 Traffic is HIGH\nGreen Signal Time : 50 secs"
    elif avg > 75 and avg <= 85:
        msg = "🚦 Traffic is MODERATE\nGreen Signal Time : 40 secs"
    elif avg > 50 and avg <= 75:
        msg = "🚦 Traffic is LOW\nGreen Signal Time : 30 secs"
    else:
        msg = "🚦 Traffic is VERY LOW\nGreen Signal Time : 20 secs"

    output_text.config(text=msg)


def exit_app():
    main.destroy()


# ---------------- UI DESIGN ----------------

# Top bar (thin)
topbar = Frame(main, bg=TOP_BG, height=50, highlightbackground=BORDER_CLR, highlightthickness=1)
topbar.pack(fill=X)

title = Label(
    topbar,
    text="Density Based Smart Traffic Control System  Using Canny Edge Detection",
    bg=TOP_BG, fg=TOP_FG,
    font=("times", 16, "bold")
)
title.pack(pady=10)

# Container Frame
container = Frame(main, bg=RIGHT_BG)
container.pack(fill=BOTH, expand=True)

# Left Menu Frame
left_frame = Frame(container, width=350, bg=LEFT_BG, highlightbackground=BORDER_CLR, highlightthickness=1)
left_frame.pack(side=LEFT, fill=Y)

# Right Output Frame
right_frame = Frame(container, bg=RIGHT_BG)
right_frame.pack(side=RIGHT, expand=True, fill=BOTH)

# ---------------- LEFT SIDE MENU ----------------

menu_title = Label(
    left_frame,
    text="Navigation Menu",
    bg=LEFT_BG, fg=SUBTEXT_FG,
    font=("times", 15, "bold")
)
menu_title.pack(pady=(20, 10))

btn_font = ("times", 13, "bold")

def style_button(btn):
    btn.config(
        bg=BTN_BG,
        fg=BTN_FG,
        activebackground=BTN_ACTIVE,
        activeforeground=BTN_FG,
        bd=1,
        relief="solid",
        highlightthickness=0
    )

upload_btn = Button(left_frame, text="Upload Traffic Image", command=uploadTrafficImage, width=28)
upload_btn.pack(pady=10)
upload_btn.config(font=btn_font)
style_button(upload_btn)

process_btn = Button(left_frame, text="Apply Canny Preprocessing", command=applyCanny, width=28)
process_btn.pack(pady=10)
process_btn.config(font=btn_font)
style_button(process_btn)

pixel_btn = Button(left_frame, text="White Pixel Count", command=pixelcount, width=28)
pixel_btn.pack(pady=10)
pixel_btn.config(font=btn_font)
style_button(pixel_btn)

time_btn = Button(left_frame, text="Green Signal Time Allocation", command=timeAllocation, width=28)
time_btn.pack(pady=10)
time_btn.config(font=btn_font)
style_button(time_btn)

exit_btn = Button(
    left_frame, text="Exit", command=exit_app, width=28,
    bg=EXIT_BG, fg=EXIT_FG,
    activebackground=EXIT_ACTIVE, activeforeground=EXIT_FG,
    bd=1, relief="solid"
)
exit_btn.pack(pady=10)
exit_btn.config(font=btn_font)

pathlabel = Label(left_frame, text="No file selected", bg=LEFT_BG, fg=SUBTEXT_FG, wraplength=320)
pathlabel.pack(pady=20)

# ---------------- RIGHT SIDE OUTPUT ----------------

output_title = Label(
    right_frame,
    text="Output Area",
    bg=RIGHT_BG, fg=TEXT_FG,
    font=("times", 16, "bold")
)

# ✅ NEW: Frame to hold 2 images side-by-side
images_frame = Frame(right_frame, bg=RIGHT_BG)
images_frame.pack(pady=0)

# ✅ Image Label 1 (Original)
image_label1 = Label(images_frame, bg=RIGHT_BG)
image_label1.pack(side=LEFT, padx=10)

# ✅ Image Label 2 (Canny Output)
image_label2 = Label(images_frame, bg=RIGHT_BG)
image_label2.pack(side=LEFT, padx=10)

output_text = Label(
    right_frame,
    text="",
    bg=RIGHT_BG, fg=SUBTEXT_FG,
    font=("times", 14),
    justify=LEFT
)

# Hide output title and text at start
hide_output_ui()

# ✅ Default image at start (FULL COVER)
if os.path.exists("assets/home.png"):
    show_full_background("assets/home.png")
else:
    show_output_ui()
    output_text.config(text="⚠️ Please add default image: assets/home.png")

main.mainloop()
