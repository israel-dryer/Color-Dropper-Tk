"""
    Color Eyedropper

    Author: Israel Dryer
    Modified: 2020-06-29
    MOdified: 2022-12-29 by Marrek Nožka

    Instructions:
        > Hover over the color you want to inspect.
        > Scroll the mouse wheel to zoom in or out.
        > Left-click to save color to clipboard and exit the program.
        > Right-click to toggle between HEX and RGB color formats.

    NOTES: There is a bug in Tkinter that prevents the Tk clipboard from
    transferring to the system clipboard when the window is destroyed, at least
    on Windows. There are a few work-arounds for this, but none of them worked
    for me. Thus, I am forced to use pyperclip to implement this functionality
    when the window is destroyed. ---> https://bugs.python.org/issue23760

"""

import tkinter as tk
from PIL import ImageGrab, ImageTk, Image
import distutils.spawn
import subprocess


class ColorDropper(tk.Tk):
    def __init__(self):
        super().__init__()
        self.wm_attributes("-fullscreen", "true")
        self.canvas = tk.Canvas(self, cursor="plus")
        self.img_data = ImageGrab.grab()
        self.img = ImageTk.PhotoImage(self.img_data)
        self.mode = "rgb"
        self.zoom = 2
        self.canvas.create_image(0, 0, image=self.img, anchor="nw")
        self.canvas.pack(fill="both", expand="yes")

        # event binding
        self.bind("<Motion>", self.on_motion)
        self.bind("<Button-1>", self.on_left_click)
        self.bind("<Button-3>", self.on_right_click)
        self.bind("<MouseWheel>", self.on_mouse_scroll)
        self.bind("<Button-4>", self.on_mouse_donw)
        self.bind("<Button-5>", self.on_mouse_up)

        # initial setup
        self.snip = None
        self.box_data = None
        self.box_img = None
        self.after(50, self.show_toplevel)

    def on_mouse_scroll(self, event):
        delta = event.delta / -120
        if delta > 0 and self.zoom < 10:
            self.zoom += delta
        elif delta < 0 and self.zoom > 0:
            self.zoom += delta
        self.on_motion()

    def on_mouse_up(self, event: tk.Event):
        if self.zoom < 10:
            self.zoom += 1
        self.on_motion()

    def on_mouse_donw(self, event: tk.Event):
        if self.zoom > 0:
            self.zoom -= 1
        self.on_motion()

    def on_left_click(self, event):
        color = "rgb" + self.snip.color_var.get()
        print(color)

        if distutils.spawn.find_executable("xclip"):
            subprocess.run(["xclip", "-i"], input=color.encode("utf8"))
        elif distutils.spawn.find_executable("xsel"):
            subprocess.run(["xsel", "--input"], input=color.encode("utf8"))
        elif distutils.spawn.find_executable("clip"):
            subprocess.run(["clip"], input=color.encode("utf8"))
        else:
            import pyperclip

            print("I use module pyperclip.")
            pyperclip.copy(color)
        self.destroy()

    def on_right_click(self, event):
        """Callback for right-click event. Toggle between hex and rgb color mode"""
        self.mode = "hex" if self.mode == "rgb" else "rgb"
        self.on_motion()

    def on_motion(self, event=None):
        """Callback for mouse motion"""
        # get current mouse position
        x, y = self.winfo_pointerxy()
        # move snip window
        self.snip.geometry(f"+{x+50}+{y-25}")
        # update the snip image
        bbox = (x - self.zoom, y - self.zoom, x + self.zoom + 1, y + self.zoom + 1)
        self.box_data = self.img_data.crop(bbox).resize((100, 100), Image.Resampling.BOX)
        self.box_img = ImageTk.PhotoImage(self.box_data)
        self.snip.canvas.create_image(0, 0, image=self.box_img, anchor="nw")
        # update color text
        text_color = self.get_colors()
        self.snip.canvas.create_text(25, 25, text="+", fill=text_color)

    def get_colors(self):
        """Extract the color from the target pixel"""
        if self.mode == "rgb":
            r, g, b = self.box_data.getpixel((25, 25))
            rgb_color = f"({r},{g},{b})"
            self.snip.color_var.set(rgb_color)
            offset = 255 - max(r, g, b)
        else:
            r, g, b = self.box_data.getpixel((25, 25))
            hex_color = f"#{255-r:0>2x}{255-g:0>2x}{255-b:0>2x}"
            self.snip.color_var.set(hex_color)
            offset = 255 - max(r, g, b)
        return f"#{offset:0>2x}{offset:0>2x}{offset:0>2x}"

    def show_toplevel(self):
        """Display the toplevel Snip widget"""
        self.snip = Snip(self)
        self.on_motion()


class Snip(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master, cursor="plus")
        self.transient(master)
        self.overrideredirect(True)
        self.geometry("180x100")
        self.lift()
        self.canvas = tk.Canvas(self, height=100, width=100)
        self.canvas.create_text(10, 10, text="+", fill="white")
        self.color_var = tk.StringVar()
        self.color_lbl = tk.Label(self, textvariable=self.color_var, font="-size 14")

        # add widget to window
        self.canvas.pack(side="left", fill="both")
        self.color_lbl.pack(side="left", fill="both", expand="yes")


if __name__ == "__main__":

    e = ColorDropper()
    e.mainloop()
