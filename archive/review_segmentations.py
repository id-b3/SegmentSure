import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, IntVar, StringVar
import os
from PIL import Image, ImageTk
import pandas as pd


image_filenames = os.listdir("./Segmentation_Check/")
df_error = pd.read_csv("./list_scans_with_seg_errors.csv")
# df_error = df_error.loc[df_error.bp_err_reviewed == 0]
df_error["bp_err_reviewed"] = 0
df_error["bp_err_reason"] = ""

# Create the root window
root = tk.Tk()
w, h = root.winfo_screenwidth(), root.winfo_screenheight()
root.geometry("%dx%d+0+0" % (w, h))

default_font = tkFont.nametofont("TkDefaultFont")
default_font.configure(size=48)
root.option_add("*Font", default_font)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.columnconfigure(3, weight=1)
root.columnconfigure(4, weight=1)

# Create a label that will hold the image
image_label = tk.Label(root)
image_label.grid(column=0, row=0, columnspan=5)

tlv_label = tk.Label(root, text="TLV: ")
tav_label = tk.Label(root, text="TAV: ")
tac_label = tk.Label(root, text="TAC: ")

tlv_label.grid(column=1, row=2)
tav_label.grid(column=2, row=2)
tac_label.grid(column=3, row=2)

# Image Index
im_idx = 0
errvar = IntVar()
errvar.set(1)

# Create Dropdown
reasonvar = StringVar()
reason = ttk.Combobox(state="readonly", textvariable=reasonvar, values=["Discontinuous", "Expiratory", "Leaks", "Other"])
reason.current(0)
reason.grid(column=1, row=4, columnspan=3)
err_box = tk.Checkbutton(root, text="SegErr", variable=errvar, onvalue=1, offvalue=0)
err_box.grid(column=1, row=3)


def set_review():
    df_error.at[im_idx, "bp_err_reviewed"] = 1
    df_error.at[im_idx, "bp_seg_error"] = errvar.get()
    if errvar.get() == 1:
        df_error.at[im_idx, "bp_err_reason"] = reasonvar.get()
    else:
        df_error.at[im_idx, "bp_err_reason"] = ""


def show_image(pid):
    pid = str(int(pid))
    if any(pid in s for s in image_filenames):
        matching = [s for s in image_filenames if pid in s]
        image = Image.open(f"./Segmentation_Check/{matching[0]}")
        photo_image = ImageTk.PhotoImage(image)
        image_label.configure(image=photo_image)
        image_label.image = photo_image
    else:
        print(f"{pid} segmentation image not found")


def show_values():
    tlv = df_error.iloc[im_idx]['bp_tlv']
    tav = df_error.iloc[im_idx]['bp_airvol']
    tac = df_error.iloc[im_idx]['bp_tcount']
    if tlv < 3.5 or tlv > 8.0:
        tlv_col = "red"
    else:
        tlv_col = "black"
    if tav < 0.08 or tav > 0.4:
        tav_col = "red"
    else:
        tav_col = "black"
    if tac < 150 or tac > 400:
        tac_col = "red"
    else:
        tac_col = "black"

    tlv_label.config(text=f"TLV: {tlv}", fg=tlv_col)
    tav_label.config(text=f"TAV: {tav}", fg=tav_col)
    tac_label.config(text=f"TAC: {tac}", fg=tac_col)
    if df_error.iloc[im_idx]['bp_seg_error'] == 1:
        err_box.select()
    else:
        err_box.deselect()


# Create a function that will be called when the "Prev" button is clicked
def on_prev_click():
    global im_idx
    im_idx -= 1
    show_image(df_error.iloc[im_idx]["participant_id"])
    show_values()


# Create a function that will be called when the "Next" button is clicked
def on_next_click():
    set_review()
    global im_idx
    im_idx += 1
    show_image(df_error.iloc[im_idx]["participant_id"])
    show_values()


show_image(df_error.iloc[im_idx]["participant_id"])
show_values()

# Create the "Prev" button
prev_button = tk.Button(root, text="Prev", command=on_prev_click, font=('Arial', 26))
prev_button.grid(column=1, row=1)

# Create the "Next" button
next_button = tk.Button(root, text="Next", command=on_next_click, font=('Arial', 26))
next_button.grid(column=3, row=1)

def key_pressed(event):
    if event.char == "p":
        on_prev_click()
    elif event.char == "n":
        on_next_click()
    elif event.char == "a":
        err_box.toggle()
    elif event.char == "d":
        reason.current(0)
    elif event.char == "e":
        reason.current(1)
    elif event.char == "l":
        reason.current(2)
    elif event.char == "o":
        reason.current(3)
    elif event.char == "s":
        df_error.to_csv("Reviewed_segmentations.csv", index=False)


# Set up keyboard shortcuts
root.bind("<KeyPress>", key_pressed)

# Start the GUI event loop
root.mainloop()

