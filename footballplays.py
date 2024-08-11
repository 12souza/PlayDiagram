import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageDraw, ImageTk, ImageGrab
import pygetwindow as gw
import pyautogui
import io
import webbrowser
import math
import json
#import qrcode



class DonationDialog(tk.Toplevel):
    def __init__(self, parent, donation_info):
        super().__init__(parent)

        self.title("Donate")
        self.geometry("300x150")

        label = tk.Label(self, text="Dontations are not required to run the program\nHowever, if you would like to donate, click below..", padx=10, pady=10)
        label.pack()

        text_widget = tk.Text(self, wrap=tk.WORD, height=2, width=40)
        text_widget.insert(tk.END, donation_info)
        text_widget.tag_add("hyperlink", "1.0", "1.end")
        text_widget.tag_config("hyperlink", foreground="blue", underline=True)
        text_widget.bind("<Button-1>", self.open_link)
        text_widget.pack(padx=10, pady=10)

    def open_link(self, event):
        webbrowser.open(event.widget.get("1.0", "1.end"), new=2)

class FootballPlayApp:
    def __init__(self, root):
        self.preview_player = None  # Variable to store the ID of the preview player
        self.preview_line = None  # Variable to store the ID of the preview line

        self.root = root
        self.root.title("Football Play Creator")
        self.root.resizable(False, False)
        self.qr_code_img = None

        self.restore_field_button = tk.Button(root, text="Restore Football Field", command=self.restore_football_field, width=20, height=2, borderwidth=3, relief=tk.SOLID)
        self.restore_field_button.place(x=10, y=0)

        self.remove_field_button = tk.Button(root, text="Remove Football Field", command=self.remove_football_field, width=20, height=2, borderwidth=3, relief=tk.SOLID)
        self.remove_field_button.place(x=10, y=50)  # Adjust the y-coordinate as needed

        self.restore_bball_button = tk.Button(root, text="Restore Basketball Court", command=self.restore_bball_field, width=20, height=2, borderwidth=3, relief=tk.SOLID)
        self.restore_bball_button.place(x=10, y=125)

        self.remove_bball_button = tk.Button(root, text="Remove Basketball Court", command=self.remove_bball_field, width=20, height=2, borderwidth=3, relief=tk.SOLID)
        self.remove_bball_button.place(x=10, y=175)  # Adjust the y-coordinate as needed

        self.delete_non_players_button = tk.Button(root, text="Delete Lines", command=self.delete_non_players, width=20, height=2, borderwidth=3, relief=tk.SOLID)
        self.delete_non_players_button.place(x=10, y=250)  # Adjust the y-coordinate as needed

        self.delete_non_players_button = tk.Button(root, text="Delete Players", command=self.delete_players, width=20, height=2, borderwidth=3, relief=tk.SOLID)
        self.delete_non_players_button.place(x=10, y=300)  # Adjust the y-coordinate as needed

        self.delete_non_players_button = tk.Button(root, text="Clear All", command=self.clearall, width=20, height=2, borderwidth=3, relief=tk.SOLID)
        self.delete_non_players_button.place(x=10, y=350)  # Adjust the y-coordinate as needed

        self.remove_bball_button = tk.Button(root, text="Donate", command=self.show_dialog, width=20, height=2, borderwidth=3, relief=tk.SOLID)
        self.remove_bball_button.place(x=10, y=450)  # Adjust the y-coordinate as needed

        self.save_image_button = tk.Button(root, text="Save as Image", command=self.save_as_image, width=18, height=2, borderwidth=3, relief=tk.SOLID)
        self.save_image_button.place(x=1100, y=0)

        self.save_image_button = tk.Button(root, text="Undo", command=self.undo, width=18, height=2, borderwidth=3, relief=tk.SOLID)
        self.save_image_button.place(x=1100, y=50)

        self.mode_label = tk.Label(root, text="Mode: X", padx=10, pady=10, justify="left")
        self.mode_label.place(x=0, y=565)

        self.text_button = tk.Button(root, text="Add Text", command=self.add_text, width=18, height=2, borderwidth=3, relief=tk.SOLID)
        self.text_button.place(x=1100, y=505)

        self.text_button = tk.Button(root, text="Shade Right", command=self.shaderight, width=18, height=2, borderwidth=3, relief=tk.SOLID)
        self.text_button.place(x=1100, y=405)

        self.text_button = tk.Button(root, text="Shade Left", command=self.shadeleft, width=18, height=2, borderwidth=3, relief=tk.SOLID)
        self.text_button.place(x=1100, y=455)

        self.text_button = tk.Button(root, text="Shade None", command=self.shadenone, width=18, height=2, borderwidth=3, relief=tk.SOLID)
        self.text_button.place(x=1100, y=355)
        self.text_button = tk.Button(root, text="Add Off-Line", command=self.addOline, width=18, height=2, borderwidth=3, relief=tk.SOLID)
        self.text_button.place(x=1100, y=305)
        

        # Load and enlarge background image
        self.field_image = tk.PhotoImage(file="football_field5.png")
        self.enlarged_image = self.field_image.zoom(1, 1)  # Adjust the zoom factors as needed
        self.field_image = tk.PhotoImage(file="bball_court.png")
        self.enlarged_imagebball = self.field_image.zoom(2, 2)  # Adjust the zoom factors as needed

        # Create canvas with enlarged background image
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.field_image_id = self.canvas.create_image(400, 300, image=self.enlarged_image, tags="field")  # Center the image
        self.field_image_idbball = None
        self.canvas.pack()

        self.canvas.bind("<ButtonRelease-1>", self.release_button)
        self.canvas.bind("<B1-Motion>", self.draw_player)
        self.canvas.bind("<ButtonPress-1>", self.press_button)
        self.canvas.bind("<ButtonRelease-1>", self.release_button)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_right_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)
        self.root.bind("<KeyPress-d>", self.delete_closest_element)

        self.players = []
        self.starting_point = None
        self.current_player = "X"
        self.line_mode = None
        self.shade = None
        self.current_color = "black"  # Default color
        self.line_width = 4  # Default line width
        triangle_image = Image.open("triangle.png")
        triangle_image = triangle_image.resize((50, 40), Image.BICUBIC)
        self.triangle_image = ImageTk.PhotoImage(triangle_image)
        # Buttons for choosing X or O
        self.x_button = tk.Button(root, text="X", command=lambda: self.set_current_player("X"), width=10, height=4, borderwidth=3, relief=tk.SOLID)
        self.x_button.pack(side=tk.LEFT, padx=5)
        self.o_button = tk.Button(root, text="O", command=lambda: self.set_current_player("O"), width=10, height=4, borderwidth=3, relief=tk.SOLID)
        self.o_button.pack(side=tk.LEFT, padx=5)
        self.tri_buttonimage = self.triangle_image
        self.tri_button = tk.Button(root, text="", command=lambda: self.set_current_player("Triangle"), width=75, height=65, borderwidth=3, relief=tk.SOLID, image=self.triangle_image)
        self.tri_button.pack(side=tk.LEFT, padx=5)
        self.pink_button = tk.Button(root, text="Dotted O", command=lambda: self.set_current_player("Dotted O"), width=10, height=4, borderwidth=3, relief=tk.SOLID)
        self.pink_button.pack(side=tk.LEFT, padx=5)

        # Buttons for drawing lines
        self.line_button = tk.Button(root, text="Line", command=self.set_line_mode, width=10, height=4, borderwidth=3, relief=tk.SOLID)
        self.line_button.pack(side=tk.LEFT, padx=5)
        self.arrow_line_button = tk.Button(root, text="Arrow Line", command=self.set_arrow_line_mode, width=10, height=4, borderwidth=3, relief=tk.SOLID)
        self.arrow_line_button.pack(side=tk.LEFT, padx=5)
        self.arrow_line_button = tk.Button(root, text="Dotted Line", command=self.set_dotted_line, width=10, height=4, borderwidth=3, relief=tk.SOLID)
        self.arrow_line_button.pack(side=tk.LEFT, padx=5)


        # Buttons for choosing colors
        self.red_button = tk.Button(root, text="Red", command=lambda: self.set_current_color("red"), width=10, height=4, bg="red", borderwidth=3, relief=tk.SOLID)
        self.red_button.pack(side=tk.LEFT, padx=5)
        
        self.blue_button = tk.Button(root, text="Blue", command=lambda: self.set_current_color("blue"), width=10, height=4,bg="blue", borderwidth=3, relief=tk.SOLID)
        self.blue_button.pack(side=tk.LEFT, padx=5)
        self.orange_button = tk.Button(root, text="Orange", command=lambda: self.set_current_color("orange"), width=10, height=4, bg="orange", borderwidth=3, relief=tk.SOLID)
        self.orange_button.pack(side=tk.LEFT, padx=5)
        self.yellow_button = tk.Button(root, text="Yellow", command=lambda: self.set_current_color("yellow"), width=10, height=4, bg="yellow", borderwidth=3, relief=tk.SOLID)
        self.yellow_button.pack(side=tk.LEFT, padx=5)
        self.purple_button = tk.Button(root, text="Purple", command=lambda: self.set_current_color("purple"), width=10, height=4,bg="purple", borderwidth=3, relief=tk.SOLID)
        self.purple_button.pack(side=tk.LEFT, padx=5)
        self.purple_button = tk.Button(root, text="Green", command=lambda: self.set_current_color("green"), width=10, height=4,bg="green", borderwidth=3, relief=tk.SOLID)
        self.purple_button.pack(side=tk.LEFT, padx=5)
        self.purple_button = tk.Button(root, text="Black", command=lambda: self.set_current_color("black"), width=10, height=4, borderwidth=3, relief=tk.SOLID)
        self.purple_button.pack(side=tk.LEFT, padx=5)


    def draw_dotted_circle(self, x, y, radius, dash_length=5):
    # Calculate the coordinates for the points of the dotted circle
        points = []
        for angle in range(0, 360, dash_length):
            radian_angle = math.radians(angle)
            points.append(x + radius * math.cos(radian_angle))
            points.append(y - radius * math.sin(radian_angle))

        # Create the polygon using the calculated points
        dotted_circle_id = self.canvas.create_polygon(points, outline=self.current_color, width=3)

        return dotted_circle_id

    def delete_non_players(self):
        # Iterate through all elements on the canvas
        for element_id in self.canvas.find_all():
            # Check if the element is a player (X, O, or Dotted O)
            tags = self.canvas.gettags(element_id)
            if "line" in tags:
                # Delete the element if it's not a player
                self.canvas.delete(element_id)
                if element_id in self.players:
                    self.players.remove(element_id)

    def delete_players(self):
        # Iterate through all elements on the canvas
        for element_id in self.canvas.find_all():
            # Check if the element is a player (X, O, or Dotted O)
            tags = self.canvas.gettags(element_id)
            if "player" in tags:
                # Delete the element if it's not a player
                self.canvas.delete(element_id)
                if element_id in self.players:
                    self.players.remove(element_id)

    def clearall(self):
        # Iterate through all elements on the canvas
        for element_id in self.canvas.find_all():
            # Check if the element is a player (X, O, or Dotted O)
            tags = self.canvas.gettags(element_id)
            if "field" not in tags:
                self.canvas.delete(element_id)
                if element_id in self.players:
                    self.players.remove(element_id)

    '''def add_text(self):
        text_input = simpledialog.askstring("Add Text", "Enter your text:")
        if text_input:
            x, y = 400, 300  # You can set the default position or use the mouse position
            text_id = self.canvas.create_text(x, y, text=text_input, font=("Arial", 14, "bold"), fill=self.current_color, tags="text")
            self.players.append(text_id)'''
    
    def add_text(self):
        text_input = simpledialog.askstring("Add Text", "Enter your text:")
        if text_input:
            # Open a dialog box to input text
            dialog = tk.Toplevel()
            dialog.title("Enter Text")
            
            # Increase the width and height of the Text widget
            text_widget = tk.Text(dialog, wrap=tk.WORD, width=60, height=15, font=("Arial", 12))
            text_widget.insert(tk.END, text_input)
            text_widget.pack(padx=10, pady=10)

            def insert_text():
                # Insert the text from the Text widget into the canvas
                text = text_widget.get("1.0", tk.END)
                x, y = 225, 20  # You can set the default position or use the mouse position
                

                # Create a semi-transparent black rectangle behind the text
                text_id = self.canvas.create_text(x, y, text=text, font=("Arial", 12, "bold"), fill="black", tags="text", width=600, anchor="nw", justify="left")  # Set a specific width to maintain wrapping
                text_bbox = self.canvas.bbox(text_id)
                padding_top = 5  # Set the padding around the text
                padding_bottom = -5  # Set the padding only for the bottom of the text
                rect_item = self.canvas.create_rectangle(text_bbox[0] - padding_top, text_bbox[1] - padding_top, text_bbox[2] + padding_top, text_bbox[3] + padding_bottom, outline="black", fill="white", width=3)  # Adjust the rectangle dimensions with padding
                self.canvas.tag_raise(text_id,rect_item)
                #text_background_id = self.canvas.create_rectangle(text_bbox, fill="black")  # Semi-transparent black color
                #self.canvas.itemconfig(text_background_id, stipple="gray50")
                
                # Raise the text above the background box
                self.canvas.tag_raise(text_id)
                
                # Add a black outline around the text
                #self.canvas.itemconfig(text_id, outline="black")
                
                self.players.append(rect_item)  # Store the background ID
                self.players.append(text_id)  # Store the text ID
                dialog.destroy()

            ok_button = tk.Button(dialog, text="OK", command=insert_text)
            ok_button.pack(pady=5)


    
    def delete_closest_element(self, event):

        x = self.canvas.canvasx(event.x) - 250.0
        y = self.canvas.canvasy(event.y)

        closest_player_id = self.find_closest_player(x, y)

        if closest_player_id:
            # Print information for debugging
            print(f"Deleting closest element with ID {closest_player_id}")
            player_coords = self.canvas.coords(closest_player_id)
            print(f"Element coordinates: {player_coords} Mouse Coordinates: ({x}, {y})")

            # Implement your deletion logic here
            self.canvas.delete(closest_player_id)
            self.players.remove(closest_player_id)

    def on_right_click(self, event):
        closest_player_id = self.find_closest_player(event.x, event.y)

        if closest_player_id:
            # Right-clicked on the closest player, initiate dragging
            self.dragging_player_id = closest_player_id
            self.drag_start = (event.x, event.y)
            print(f"{closest_player_id} grabbed")

    def on_right_drag(self, event):
        if hasattr(self, 'dragging_player_id') and self.dragging_player_id is not None:
            # Dragging the player, move it to the current mouse position
            delta_x = event.x - self.drag_start[0]
            delta_y = event.y - self.drag_start[1]

            # Move the player to the new position
            self.canvas.move(self.dragging_player_id, delta_x, delta_y)

            # Update the drag start position for the next movement
            self.drag_start = (event.x, event.y)

    def on_right_release(self, event):
        # Stop dragging when the right mouse button is released
        self.dragging_player_id = None

    def find_closest_player(self, x, y):
        closest_player_id = None
        closest_distance = float('inf')  # Initialize with positive infinity

        for player_id in self.players:
            # Get the coordinates of the player
            player_coords = self.canvas.coords(player_id)

            # Calculate the distance from the given coordinates to the player
            distance = ((x - player_coords[0]) ** 2 + (y - player_coords[1]) ** 2) ** 0.5

            # Update the closest player if the current player is closer
            if distance < closest_distance:
                closest_player_id = player_id
                closest_distance = distance

        return closest_player_id
        
    def draw_player(self, event):
        x, y = event.x, event.y
        if self.line_mode in {"Line", "Arrow Line", "Dotted Line"} and self.starting_point:
            self.canvas.delete("preview_line")  # Delete the previous preview line
            start_x, start_y = self.starting_point
            if self.line_mode == "Line":
                self.preview_line = self.canvas.create_line(start_x, start_y, x, y, width=self.line_width, fill=self.current_color, tags="preview_line")
            elif self.line_mode == "Arrow Line":
                self.preview_line = self.canvas.create_line(start_x, start_y, x, y, arrow=tk.LAST, width=self.line_width, fill=self.current_color, tags="preview_line")
            elif self.line_mode == "Dotted Line":
                dash_length = 5  # Adjust the dash length as needed
                dash_count = int(((x - start_x) ** 2 + (y - start_y) ** 2) ** 0.5 / dash_length)
                dash = [dash_length, dash_length]
                self.preview_line = self.canvas.create_line(start_x, start_y, x, y, dash=dash, arrow=tk.LAST, width=self.line_width, fill=self.current_color, tags="preview_line")
        elif self.current_player in {"X", "O"} and self.preview_player:
            # Update the position of the preview player as the mouse moves
            if(self.current_player == "X"):
                self.canvas.coords(self.preview_player, x, y)
            elif (self.current_player == "O"):
                radius = 15
                x1, y1 = x - radius, y - radius
                x2, y2 = x + radius, y + radius
                self.canvas.coords(self.preview_player, x1, y1, x2, y2)
        elif self.current_player == "Dotted O" and self.preview_player:
            radius = 30
            dash_length = 5  # Adjust the dash length as needed
            dash_count = int(2 * math.pi * radius / dash_length)
            dash = [dash_length, dash_length]
            # Provide all four coordinates for create_oval
            x1, y1 = x - radius, y - radius
            x2, y2 = x + radius, y + radius
            self.canvas.coords(self.preview_player, x1, y1, x2, y2)
        elif self.current_player == "Triangle":
            triangle_coords = [x - 15, y, x + 15, y, x, y + 30]
            self.canvas.coords(self.preview_player, triangle_coords)

    def undo(self):
        if self.players:
            # Undo the last drawn element
            last_element = self.players.pop()
            tags = self.canvas.gettags(last_element)
            if "line" in tags:  # Check if it's a line
                self.canvas.delete(last_element)
            else:  # It's a player
                self.canvas.delete(last_element)

    #https://www.paypal.com/donate/?business=JAMDBQ7HT859S&no_recurring=0&currency_code=USD
    def show_dialog(self):
        donation_info = "https://www.paypal.com/donate/?business=JAMDBQ7HT859S&no_recurring=0&currency_code=USD"
        
        DonationDialog(self.root, donation_info)

    def press_button(self, event):
        if self.line_mode == "Line" or self.line_mode == "Arrow Line" or self.line_mode == "Dotted Line":
            self.starting_point = (event.x, event.y)
        elif self.current_player in {"X", "O", "Dotted O", "Triangle"}:
            x, y = event.x, event.y
            # Show the preview for X or O only in X or O mode
            if self.current_player in {"X", "O"}:
                if self.current_player == "X":
                    self.preview_player = self.canvas.create_text(x, y, text=self.current_player, font=("Arial", 24), fill=self.current_color, tags="player")
                elif self.current_player == "O":
                    radius = 15
                    self.preview_player = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                                fill="white", width=3, outline="black", tags="player")
                
            elif self.current_player == "Dotted O":
                radius = 20
                dash_length = 5  # Adjust the dash length as needed
                dash_count = int(2 * math.pi * radius / dash_length)
                dash = [dash_length, dash_length]
                # Provide all four coordinates for create_oval
                self.preview_player = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, dash=dash, width=3, outline="black")
            elif self.current_player == "Triangle":
                triangle_coords = [x - 15, y, x + 15, y, x, y + 30]  # Coordinates for the triangle vertices
                self.preview_player = self.canvas.create_polygon(triangle_coords, fill="white", outline="black")



    def release_button(self, event):
        shade_id = None
        if self.line_mode in {"Line", "Arrow Line", "Dotted Line"}:
            x, y = event.x, event.y
            if self.starting_point and (self.line_mode == "Line" or self.line_mode == "Arrow Line" or self.line_mode == "Dotted Line"):
                start_x, start_y = self.starting_point
            if self.line_mode == "Line":
                line_id = self.canvas.create_line(start_x, start_y, x, y, arrow=tk.NONE, width=self.line_width, fill=self.current_color, tags="line")
                self.players.append(line_id)
            elif self.line_mode == "Arrow Line":
                line_id = self.canvas.create_line(start_x, start_y, x, y, arrow=tk.LAST, width=self.line_width, fill=self.current_color, tags="line")
                self.players.append(line_id)
            elif self.line_mode == "Dotted Line":
                dash_length = 5  # Adjust the dash length as needed
                dash_count = int(((x - start_x) ** 2 + (y - start_y) ** 2) ** 0.5 / dash_length)
                dash = [dash_length, dash_length]
                line_id = self.canvas.create_line(start_x, start_y, x, y, dash=dash, arrow=tk.NONE, width=self.line_width, fill=self.current_color, tags="line")
                self.players.append(line_id)
            self.starting_point = None
            # Save the preview line on release when in line mode
            '''if self.preview_line:
                #self.players.append(self.preview_line)  # Store the line ID in the players list'''
            self.canvas.delete("preview_line")
        elif self.current_player in {"X", "O", "Dotted O", "Triangle"} and self.preview_player:
            # Create the actual player and reset the preview
            x, y = event.x, event.y
            radius = 15
            if self.current_player == "O":
                if self.current_color != "black":
                    # Use create_oval to create a filled oval (circle)
                    
                    player_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                                fill=self.current_color, width=3, outline="black", tags="player")
                else:
                    player_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                                fill="white", width=3, outline="black", tags="player")
                
                if self.shade in ("left", "right"):
                    # Create the white oval to cover half of the filled oval
                    #start_angle = -90  # right side
                    radius = 15
                    if self.shade == "left":
                        start_angle = 90 # left side
                    elif self.shade == "right":
                        start_angle = -90
                    extent_angle = 180  # Extent angle of the arc (180 for a semicircle)
                    # Calculate the coordinates for the points of the semicircle
                    points = []
                    for angle in range(start_angle, start_angle + extent_angle + 1):
                        radian_angle = math.radians(angle)
                        points.append(x + radius * math.cos(radian_angle))
                        points.append(y - radius * math.sin(radian_angle))

                    # Create the polygon using the calculated points
                    shade_id = self.canvas.create_polygon(points, fill="black", outline="black", width=3, tags="player")
            elif self.current_player == "X":
                x, y = event.x, event.y
                player_id = self.canvas.create_text(x, y, text=self.current_player, font=("Arial", 24), fill=self.current_color, tags="player")
            elif self.current_player == "Dotted O":
                radius = 30
                dash_length = 5  # Adjust the dash length as needed
                dash_count = int(2 * math.pi * radius / dash_length)
                dash = [dash_length, dash_length]
                player_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, dash=dash, width=3, outline="black")
                #self.players.append(dotted_circle_id)
            elif self.current_player == "Triangle":
                x, y = event.x, event.y

                # Create the downward facing triangle
                triangle_coords = [x - 15, y, x + 15, y, x, y + 30]  # Coordinates for the triangle vertices
                if(self.current_color != "black"):
                    player_id = self.canvas.create_polygon(triangle_coords, fill=self.current_color, outline="black", width=3, tags="player")
                else:
                    player_id = self.canvas.create_polygon(triangle_coords, fill="white", outline="black", width=3, tags="player")

                # Clear the preview triangle
                self.canvas.delete(self.preview_player)
                self.preview_player = None
            self.players.append(player_id)
            if shade_id:
                self.players.append(shade_id)
            self.canvas.delete(self.preview_player)
            self.preview_player = None

    def remove_football_field(self):
        # Remove the football field image from the canvas
        if self.field_image_id:
            self.canvas.delete(self.field_image_id)
            self.field_image_id = None

    def restore_football_field(self):
        # Restore the football field image on the canvas
        if not self.field_image_id:
            self.canvas.delete(self.field_image_idbball)
            self.field_image_id = self.canvas.create_image(400, 300, image=self.enlarged_image, tags="field")  # Center the image
            self.canvas.tag_lower(self.field_image_id)  # Bring the image to the back
            self.field_image_idbball = None

    def remove_bball_field(self):
        # Remove the football field image from the canvas
        if self.field_image_idbball:
            self.canvas.delete(self.field_image_idbball)
            self.field_image_idbball = None

    def restore_bball_field(self):
        # Restore the football field image on the canvas
        if not self.field_image_idbball:
            self.canvas.delete(self.field_image_id)
            self.field_image_idbball = self.canvas.create_image(400, 300, image=self.enlarged_imagebball, tags="field")  # Center the image
            self.canvas.tag_lower(self.field_image_idbball)  # Bring the image to the back
            self.field_image_id = None

    def set_current_player(self, player):
        self.current_player = player
        # Reset line mode when X or O is selected
        self.line_mode = None
        self.update_mode_label()

    def set_line_mode(self):
        self.line_mode = "Line"
        self.current_player = None
        self.update_mode_label()

    def set_arrow_line_mode(self):
        self.line_mode = "Arrow Line"
        self.current_player = None
        self.update_mode_label()

    def set_dotted_line(self):
        self.line_mode = "Dotted Line"
        self.current_player = None
        self.update_mode_label()
    
    def shaderight(self):
        self.shade = "right"

    def shadeleft(self):
        self.shade = "left"

    def shadenone(self):
        self.shade = None

    def addOline(self):
        radius = 15
        x = 300 
        y = 485
        for i in range(5):
            if i == 2:
                player_id = self.canvas.create_rectangle(x - radius, y - radius, x + radius, y + radius,
                                                      fill="white", width=3, outline="black", tags="player")
            else:
                player_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                    fill="white", width=3, outline="black", tags="player")
            x = x + 50
        
            self.players.append(player_id)
        print(self.players)

    def set_current_color(self, color):
        self.current_color = color

    def update_mode_label(self):
        mode_text = f"Mode: {self.current_player}" if self.current_player in {"X", "O", "Dotted O", "Triangle"} else f"Mode: {self.line_mode}"
        self.mode_label.config(text=mode_text)

    def save_as_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            # Get the window coordinates
            window = gw.getWindowsWithTitle("Football Play Creator")[0]
            left, top, right, bottom = window.left, window.top, window.left + window.width, window.top + window.height

            # Get the canvas coordinates relative to the window
            canvas_coords = self.canvas.bbox("all")

            # Ensure canvas coordinates are not empty
            if canvas_coords:
                canvas_left, canvas_top, canvas_right, canvas_bottom = canvas_coords

                # Calculate the offset to move the screenshot to the right (e.g., 50 pixels)
                offset = 50
                canvas_left += left + 250
                canvas_top += top + offset - 25
                canvas_right += left + 250
                canvas_bottom += top + offset - 17

                # Capture the canvas screenshot
                canvas_screenshot = ImageGrab.grab(bbox=(canvas_left, canvas_top, canvas_right, canvas_bottom))

                # Save the canvas screenshot as PNG
                canvas_screenshot.save(file_path, "PNG")
            else:
                print("Canvas is empty or coordinates are invalid.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FootballPlayApp(root)
    root.mainloop()
