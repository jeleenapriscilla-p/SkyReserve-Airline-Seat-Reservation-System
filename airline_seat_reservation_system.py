import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json

# ============================================================
# AIRLINE SEAT RESERVATION SYSTEM
# Queue + Selection Sort + Binary Search Tree + GUI
# ============================================================

# ---------------------------- DATA ----------------------------
FLIGHTS = [
    {"code": "AI101", "from": "Chennai", "to": "Delhi", "date": "15-Oct-2026", "time": "06:30 AM", "price": 5500},
    {"code": "6E205", "from": "Chennai", "to": "Mumbai", "date": "15-Oct-2026", "time": "09:15 AM", "price": 4200},
    {"code": "SG310", "from": "Chennai", "to": "Bangalore", "date": "16-Oct-2026", "time": "07:00 AM", "price": 2800},
    {"code": "AI405", "from": "Chennai", "to": "Kochi", "date": "16-Oct-2026", "time": "11:30 AM", "price": 3200},
    {"code": "6E512", "from": "Chennai", "to": "Hyderabad", "date": "17-Oct-2026", "time": "02:00 PM", "price": 3900},
    {"code": "AI620", "from": "Chennai", "to": "Kolkata", "date": "17-Oct-2026", "time": "05:45 PM", "price": 5100},
    {"code": "SG715", "from": "Chennai", "to": "Pune", "date": "18-Oct-2026", "time": "08:20 AM", "price": 4600},
    {"code": "6E830", "from": "Chennai", "to": "Goa", "date": "18-Oct-2026", "time": "01:15 PM", "price": 3700},
    {"code": "AI915", "from": "Chennai", "to": "Ahmedabad", "date": "19-Oct-2026", "time": "06:00 AM", "price": 5300},
    {"code": "SG225", "from": "Chennai", "to": "Jaipur", "date": "19-Oct-2026", "time": "10:45 AM", "price": 5800},
]

# Exact requested capacity: 10 First + 20 Business + 30 Economy = 60
# First Class: 5 rows x 2 seats (1-1)
# Business Class: 5 rows x 4 seats (1-2-1)
# Economy Class: 5 rows x 6 seats (3-3)
SEAT_LAYOUT = []
for row in range(1, 6):
    SEAT_LAYOUT.append(("First Class", row, ["A", "F"]))
for row in range(6, 11):
    SEAT_LAYOUT.append(("Business Class", row, ["A", "B", "E", "F"]))
for row in range(11, 16):
    SEAT_LAYOUT.append(("Economy Class", row, ["A", "B", "C", "D", "E", "F"]))

SEAT_CLASS = {}
for seat_class, row, letters in SEAT_LAYOUT:
    for letter in letters:
        SEAT_CLASS[f"{row}{letter}"] = seat_class

CLASS_PRICES = {"First Class": 1.80, "Business Class": 1.35, "Economy Class": 1.00}
CLASS_DISPLAY = {"First Class": "FIRST", "Business Class": "BUSINESS", "Economy Class": "ECONOMY"}

GENDER_COLORS = {"Female": "#ff8fc7", "Male": "#72b7ff", "Other": "#bdbdbd"}

@dataclass
class Passenger:
    passenger_id: str
    name: str
    age: int
    gender: str
    phone: str
    email: str
    flight_code: str
    seat: str
    seat_class: str
    fare: float
    booking_id: str

@dataclass
class BookingRequest:
    passengers: list
    requested_at: str

# ---------------------------- QUEUE ---------------------------
class BookingQueue:
    """FIFO queue implemented using a Python list, with explicit enqueue/dequeue operations."""
    def __init__(self):
        self.items = []

    def enqueue(self, request):
        self.items.append(request)

    def dequeue(self):
        if self.items:
            return self.items.pop(0)
        return None

    def peek(self):
        return self.items[0] if self.items else None

    def size(self):
        return len(self.items)

# ---------------------- BINARY SEARCH TREE --------------------
class BSTNode:
    def __init__(self, key, passenger):
        self.key = key
        self.passenger = passenger
        self.left = None
        self.right = None

class BookingBST:
    """BST indexed by Passenger ID for fast passenger-record retrieval."""
    def __init__(self):
        self.root = None

    def insert(self, key, passenger):
        self.root = self._insert(self.root, key, passenger)

    def _insert(self, node, key, passenger):
        if node is None:
            return BSTNode(key, passenger)
        if key < node.key:
            node.left = self._insert(node.left, key, passenger)
        elif key > node.key:
            node.right = self._insert(node.right, key, passenger)
        else:
            node.passenger = passenger
        return node

    def search(self, key):
        node = self.root
        while node:
            if key == node.key:
                return node.passenger
            node = node.left if key < node.key else node.right
        return None

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.passenger)
            self._inorder(node.right, result)

    def delete(self, key):
        self.root, deleted = self._delete(self.root, key)
        return deleted

    def _delete(self, node, key):
        if node is None:
            return None, False
        if key < node.key:
            node.left, deleted = self._delete(node.left, key)
            return node, deleted
        if key > node.key:
            node.right, deleted = self._delete(node.right, key)
            return node, deleted

        if node.left is None:
            return node.right, True
        if node.right is None:
            return node.left, True

        successor = self._min_node(node.right)
        node.key = successor.key
        node.passenger = successor.passenger
        node.right, _ = self._delete(node.right, successor.key)
        return node, True

    def _min_node(self, node):
        while node.left:
            node = node.left
        return node

# ------------------------- SORTING ----------------------------
def selection_sort(flights, ascending=True):
    """Selection sort by ticket price; returns a new sorted list."""
    arr = flights[:]
    n = len(arr)
    for i in range(n - 1):
        selected = i
        for j in range(i + 1, n):
            if ascending:
                if arr[j]["price"] < arr[selected]["price"]:
                    selected = j
            else:
                if arr[j]["price"] > arr[selected]["price"]:
                    selected = j
        if selected != i:
            arr[i], arr[selected] = arr[selected], arr[i]
    return arr

# ------------------------- MAIN APP ---------------------------
class AirlineApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SkyReserve - Airline Seat Reservation System")
        self.geometry("1280x820")
        self.minsize(1120, 720)
        self.configure(bg="#eef3f8")

        self.queue = BookingQueue()
        self.bst = BookingBST()
        self.booked_seats = {f["code"]: {} for f in FLIGHTS}
        self.booking_counter = 1000
        self.passenger_counter = 10000
        self.selected_flight = None
        self.selected_seats = []
        self.passenger_entries = {}
        self.seat_buttons = {}
        self.current_sort_ascending = True
        self.history = []
        self.data_file = Path(__file__).with_name("airline_reservation_data.json")

        self._load_data()

        self._setup_style()
        self._build_header()
        if self.queue.size() or self.bst.inorder():
            self.header_status.configure(text=f"Restored: {len(self.bst.inorder())} confirmed • {self.queue.size()} queued")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_sidebar()
        self._build_content_area()
        self.show_dashboard()

    # -------------------- FILE PERSISTENCE ---------------------
    def _on_close(self):
        """Save all current reservation data before closing the application."""
        self._save_data()
        self.destroy()

    def _passenger_from_dict(self, data):
        return Passenger(
            data["passenger_id"], data["name"], int(data["age"]), data["gender"],
            data["phone"], data["email"], data["flight_code"], data["seat"],
            data["seat_class"], float(data["fare"]), data.get("booking_id", "")
        )

    def _save_data(self):
        """Save bookings, queue requests, counters and history to a JSON file."""
        data = {
            "booking_counter": self.booking_counter,
            "passenger_counter": self.passenger_counter,
            "confirmed": [asdict(p) for p in self.bst.inorder()],
            "queue": [
                {
                    "passengers": [asdict(p) for p in req.passengers],
                    "requested_at": req.requested_at
                }
                for req in self.queue.items
            ],
            "history": self.history
        }
        try:
            self.data_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except OSError as exc:
            messagebox.showerror("File Error", f"Could not save reservation data.\n\n{exc}")

    def _load_data(self):
        """Load saved data at startup and rebuild the queue, BST and occupied seats."""
        if not self.data_file.exists():
            return
        try:
            data = json.loads(self.data_file.read_text(encoding="utf-8"))
            self.booking_counter = int(data.get("booking_counter", 1000))
            self.passenger_counter = int(data.get("passenger_counter", 10000))
            self.history = data.get("history", [])

            for item in data.get("confirmed", []):
                p = self._passenger_from_dict(item)
                if p.flight_code in self.booked_seats:
                    self.booked_seats[p.flight_code][p.seat] = p
                self.bst.insert(p.passenger_id, p)

            for req_data in data.get("queue", []):
                passengers = [self._passenger_from_dict(item) for item in req_data.get("passengers", [])]
                if passengers:
                    self.queue.enqueue(BookingRequest(passengers, req_data.get("requested_at", "")))
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
            messagebox.showwarning(
                "Saved Data Warning",
                f"Previous reservation data could not be loaded.\n\n{exc}\n\nThe application will start with empty current data."
            )
            self.queue = BookingQueue()
            self.bst = BookingBST()
            self.booked_seats = {f["code"]: {} for f in FLIGHTS}
            self.booking_counter = 1000
            self.passenger_counter = 10000
            self.history = []

    # ---------------------- STYLING ---------------------------
    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=10,
                        foreground="white", background="#1769aa")
        style.map("Primary.TButton", background=[("active", "#0f568e")])
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=(14, 8))

    def _build_header(self):
        header = tk.Frame(self, bg="#123b5d", height=74)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="✈  SkyReserve", bg="#123b5d", fg="white",
                 font=("Segoe UI", 22, "bold")).pack(side="left", padx=25)
        tk.Label(header, text="Airline Seat Reservation System", bg="#123b5d", fg="#d8e8f5",
                 font=("Segoe UI", 11)).pack(side="left", padx=5, pady=(7, 0))
        self.header_status = tk.Label(header, text="", bg="#123b5d", fg="#c8e6c9",
                                      font=("Segoe UI", 10, "bold"))
        self.header_status.pack(side="right", padx=25)

    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg="#173f5f", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="MAIN MENU", bg="#173f5f", fg="#a9c4d8",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=22, pady=(25, 10))
        buttons = [
            ("⌂  Dashboard", self.show_dashboard),
            ("✈  Flights & Seats", self.show_flights),
            ("🎫  New Booking", self.start_booking),
            ("▣  Booking Queue", self.show_queue),
            ("⌕  Search Booking", self.show_search),
            ("✕  Cancellation", self.show_cancel),
            ("☷  All Confirmed", self.show_confirmed),
            ("▤  Booking History", self.show_history),
        ]
        for text, command in buttons:
            b = tk.Button(self.sidebar, text=text, command=command, anchor="w",
                          bg="#173f5f", fg="white", activebackground="#245b82",
                          activeforeground="white", bd=0, relief="flat",
                          font=("Segoe UI", 10, "bold"), padx=22, pady=12)
            b.pack(fill="x", pady=1)
        tk.Label(self.sidebar, text="\nDSA COMPONENTS", bg="#173f5f", fg="#a9c4d8",
                 font=("Segoe UI", 9, "bold"), justify="left").pack(anchor="w", padx=22, pady=(18, 4))
        tk.Label(self.sidebar, text="Queue  → FIFO requests\nSelection Sort → fares\nBST → passenger records",
                 bg="#173f5f", fg="#e5eef5", justify="left", font=("Segoe UI", 9), padx=22).pack(anchor="w")

    def _build_content_area(self):
        self.content = tk.Frame(self, bg="#eef3f8")
        self.content.pack(side="left", fill="both", expand=True)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def page_title(self, title, subtitle=""):
        frame = tk.Frame(self.content, bg="#eef3f8")
        frame.pack(fill="x", padx=25, pady=(22, 12))
        tk.Label(frame, text=title, bg="#eef3f8", fg="#123b5d",
                 font=("Segoe UI", 21, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(frame, text=subtitle, bg="#eef3f8", fg="#667785",
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))

    def card(self, parent, title=None):
        frame = tk.Frame(parent, bg="white", highlightbackground="#d9e2ea", highlightthickness=1)
        if title:
            tk.Label(frame, text=title, bg="white", fg="#123b5d",
                     font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=18, pady=(15, 8))
        return frame

    # ----------------------- DASHBOARD ------------------------
    def show_dashboard(self):
        self.clear_content()
        self.page_title("Dashboard", "Manage flights, seats and passenger bookings from one place.")

        stats = tk.Frame(self.content, bg="#eef3f8")
        stats.pack(fill="x", padx=25, pady=5)
        total = sum(len(v) for v in self.booked_seats.values())
        pending = self.queue.size()
        confirmed = len(self.bst.inorder())
        available = len(FLIGHTS) * 60 - total
        cards = [("10", "Preloaded Flights", "#1769aa"), (str(available), "Available Seats", "#2e7d32"),
                 (str(pending), "Queue Requests", "#ef6c00"), (str(confirmed), "Confirmed Passengers", "#6a1b9a")]
        for value, label, color in cards:
            c = tk.Frame(stats, bg="white", highlightbackground="#d9e2ea", highlightthickness=1)
            c.pack(side="left", fill="both", expand=True, padx=5)
            tk.Label(c, text=value, bg="white", fg=color, font=("Segoe UI", 24, "bold")).pack(pady=(14, 0))
            tk.Label(c, text=label, bg="white", fg="#667785", font=("Segoe UI", 9, "bold")).pack(pady=(0, 14))

        body = tk.Frame(self.content, bg="#eef3f8")
        body.pack(fill="both", expand=True, padx=25, pady=15)
        left = self.card(body, "System Workflow")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        steps = [
            ("1", "Choose Flight", "Select one of the 10 preloaded flights."),
            ("2", "Select Seats", "Use the aircraft-style 60-seat map."),
            ("3", "Enter Passengers", "Add details for every selected seat."),
            ("4", "Queue Request", "Booking requests are processed FIFO."),
            ("5", "Confirm Booking", "Confirmed records enter the BST."),
        ]
        for num, title, desc in steps:
            row = tk.Frame(left, bg="white")
            row.pack(fill="x", padx=18, pady=8)
            tk.Label(row, text=num, bg="#1769aa", fg="white", width=3,
                     font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
            text = tk.Frame(row, bg="white")
            text.pack(side="left")
            tk.Label(text, text=title, bg="white", fg="#173f5f", font=("Segoe UI", 10, "bold")).pack(anchor="w")
            tk.Label(text, text=desc, bg="white", fg="#6b7884", font=("Segoe UI", 9)).pack(anchor="w")
        right = self.card(body, "Seat Color Legend")
        right.pack(side="right", fill="both", expand=True, padx=(8, 0))
        self._legend(right, padx=20, pady=8)
        tk.Button(right, text="Start New Booking", command=self.start_booking,
                  bg="#1769aa", fg="white", activebackground="#0f568e", bd=0,
                  font=("Segoe UI", 10, "bold"), padx=20, pady=10).pack(pady=20)

    def _legend(self, parent, padx=18, pady=4):
        items = [
            ("#e8f0f7", "Available First Class"),
            ("#eef5ed", "Available Business Class"),
            ("#f8f5eb", "Available Economy Class"),
            (GENDER_COLORS["Female"], "Booked - Female"),
            (GENDER_COLORS["Male"], "Booked - Male"),
            (GENDER_COLORS["Other"], "Booked - Other"),
            ("#4d9de0", "Selected"),
        ]
        for color, text in items:
            row = tk.Frame(parent, bg="white")
            row.pack(anchor="w", padx=padx, pady=pady)
            tk.Label(row, bg=color, width=3, height=1, relief="solid", bd=1).pack(side="left", padx=(0, 10))
            tk.Label(row, text=text, bg="white", fg="#455a64", font=("Segoe UI", 9)).pack(side="left")

    # ------------------------- FLIGHTS ------------------------
    def show_flights(self):
        self.clear_content()
        self.page_title("Flights & Seat Availability", "10 sample flights are preloaded for the project demonstration.")
        top = tk.Frame(self.content, bg="#eef3f8")
        top.pack(fill="x", padx=25)
        ttk.Button(top, text="Sort by Fare ↑↓", command=self.toggle_sort).pack(side="right")
        columns = ("code", "route", "date", "time", "fare", "available")
        tree = ttk.Treeview(self.content, columns=columns, show="headings", height=15)
        headings = {"code":"Flight", "route":"Route", "date":"Date", "time":"Departure", "fare":"Base Fare", "available":"Available Seats"}
        widths = {"code":100, "route":230, "date":130, "time":120, "fare":120, "available":150}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center")
        tree.pack(fill="both", expand=True, padx=25, pady=12)
        for f in selection_sort(FLIGHTS, self.current_sort_ascending):
            available = 60 - len(self.booked_seats[f["code"]])
            tree.insert("", "end", values=(f["code"], f["from"]+" → "+f["to"], f["date"], f["time"], f"₹{f['price']:,}", available))
        ttk.Button(self.content, text="Select Flight & View Seats", style="Primary.TButton",
                   command=lambda: self._open_selected_flight(tree)).pack(pady=(0, 15))

    def toggle_sort(self):
        self.current_sort_ascending = not self.current_sort_ascending
        self.show_flights()

    def _open_selected_flight(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Select Flight", "Please select a flight first.")
            return
        code = tree.item(selection[0])["values"][0]
        self.selected_flight = next(f for f in FLIGHTS if f["code"] == code)
        self.selected_seats = []
        self.show_seat_selection()

    # ---------------------- BOOKING FLOW ----------------------
    def start_booking(self):
        self.selected_flight = None
        self.selected_seats = []
        self.show_flights_for_booking()

    def show_flights_for_booking(self):
        self.clear_content()
        self.page_title("1. Choose Your Flight", "Select a flight to open its aircraft seat map.")
        container = tk.Frame(self.content, bg="#eef3f8")
        container.pack(fill="both", expand=True, padx=25)
        for f in FLIGHTS:
            available = 60 - len(self.booked_seats[f["code"]])
            c = tk.Frame(container, bg="white", highlightbackground="#d9e2ea", highlightthickness=1)
            c.pack(fill="x", pady=5)
            tk.Label(c, text=f["code"], bg="white", fg="#1769aa", font=("Segoe UI", 12, "bold"), width=9).pack(side="left", padx=10)
            tk.Label(c, text=f["from"]+"  →  "+f["to"], bg="white", fg="#173f5f", font=("Segoe UI", 11, "bold"), width=25, anchor="w").pack(side="left")
            tk.Label(c, text=f["date"], bg="white", fg="#667785", width=15).pack(side="left")
            tk.Label(c, text=f["time"], bg="white", fg="#667785", width=13).pack(side="left")
            tk.Label(c, text=f"₹{f['price']:,} + class", bg="white", fg="#333", width=15).pack(side="left")
            tk.Label(c, text=f"{available}/60 seats", bg="white", fg="#2e7d32", width=13).pack(side="left")
            ttk.Button(c, text="View Seats", command=lambda flight=f: self._choose_flight(flight)).pack(side="right", padx=12)

    def _choose_flight(self, flight):
        self.selected_flight = flight
        self.selected_seats = []
        self.show_seat_selection()

    def show_seat_selection(self):
        self.clear_content()
        f = self.selected_flight
        self.page_title(
            "2. Select Seats",
            f"{f['code']}  •  {f['from']} → {f['to']}  •  {f['date']}  •  {f['time']}"
        )

        main = tk.Frame(self.content, bg="#eef3f8")
        main.pack(fill="both", expand=True, padx=25, pady=5)

        # -------------------------------------------------------
        # LEFT: Scrollable aircraft seat map
        # -------------------------------------------------------
        map_card = self.card(main, "Aircraft Seat Map")
        map_card.pack(side="left", fill="both", expand=True, padx=(0, 8))

        map_outer = tk.Frame(map_card, bg="white")
        map_outer.pack(fill="both", expand=True, padx=10, pady=(5, 0))

        map_canvas = tk.Canvas(
            map_outer, bg="white", highlightthickness=0,
            xscrollincrement=1, yscrollincrement=1
        )
        map_scrollbar = ttk.Scrollbar(
            map_outer, orient="vertical", command=map_canvas.yview
        )
        map_canvas.configure(yscrollcommand=map_scrollbar.set)

        map_canvas.pack(side="left", fill="both", expand=True)
        map_scrollbar.pack(side="right", fill="y")

        aircraft = tk.Frame(
            map_canvas, bg="#f6f9fc",
            highlightbackground="#9fb3c1", highlightthickness=2,
            width=780
        )
        aircraft_window = map_canvas.create_window(
            (0, 0), window=aircraft, anchor="nw", width=780
        )

        def update_scrollregion(event=None):
            map_canvas.configure(scrollregion=map_canvas.bbox("all"))
            # Keep the aircraft centered / fitted to the available width.
            canvas_width = map_canvas.winfo_width()
            if canvas_width > 20:
                map_canvas.itemconfigure(
                    aircraft_window,
                    width=max(760, canvas_width - 4)
                )

        aircraft.bind("<Configure>", update_scrollregion)
        map_canvas.bind("<Configure>", update_scrollregion)

        # Mouse-wheel scrolling over the seat map.
        def on_mousewheel(event):
            map_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        map_canvas.bind_all("<MouseWheel>", on_mousewheel)
        map_scrollbar.bind("<MouseWheel>", on_mousewheel)

        # Aircraft nose / cockpit
        nose = tk.Frame(aircraft, bg="#dbeaf5", height=58)
        nose.pack(fill="x", padx=25, pady=(14, 5))
        nose.pack_propagate(False)
        tk.Label(
            nose, text="✈  FRONT / COCKPIT",
            bg="#dbeaf5", fg="#173f5f",
            font=("Segoe UI", 10, "bold")
        ).pack(pady=19)

        # Class legend inside the aircraft itself
        class_info = [
            ("FIRST CLASS", "Rows 1–5  •  10 seats  •  1–1 layout", "#f4d35e"),
            ("BUSINESS CLASS", "Rows 6–10  •  20 seats  •  1–2–1 layout", "#73bfe5"),
            ("ECONOMY CLASS", "Rows 11–15  •  30 seats  •  3–3 layout", "#8fbe68"),
        ]
        for title, detail, color in class_info:
            bar = tk.Frame(aircraft, bg=color, height=34)
            bar.pack(fill="x", padx=45, pady=(4, 0))
            bar.pack_propagate(False)
            tk.Label(
                bar, text=f"{title}   |   {detail}",
                bg=color, fg="#173f5f",
                font=("Segoe UI", 9, "bold")
            ).pack(pady=8)

        seat_area = tk.Frame(
            aircraft, bg="white",
            highlightbackground="#d5dde3", highlightthickness=1
        )
        seat_area.pack(fill="x", padx=45, pady=12)

        # Header showing the actual aircraft seating patterns.
        tk.Label(
            seat_area, text="ROW", bg="white", fg="#7c8b96",
            font=("Segoe UI", 8, "bold"), width=5
        ).grid(row=0, column=0, pady=7)
        for col, text in enumerate(["A", "B", "C", "AISLE", "D", "E", "F"], start=1):
            tk.Label(
                seat_area, text=text, bg="white",
                fg="#173f5f" if text != "AISLE" else "#9aa7b0",
                font=("Segoe UI", 8, "bold")
            ).grid(row=0, column=col, padx=5, pady=7)

        self.seat_buttons = {}
        for seat_class, row_number, letters in SEAT_LAYOUT:
            tk.Label(
                seat_area, text=str(row_number), bg="white", fg="#7c8b96",
                font=("Segoe UI", 9, "bold"), width=5
            ).grid(row=row_number, column=0, padx=2, pady=4)

            if seat_class == "First Class":
                # 1 - 1: one large seat on each side of the aisle.
                self._create_seat_button(seat_area, f"{row_number}A", row_number, 1, wide=True)
                tk.Label(
                    seat_area, text="AISLE", bg="white", fg="#b0bac1",
                    font=("Segoe UI", 8, "bold"), width=16
                ).grid(row=row_number, column=2, columnspan=4)
                self._create_seat_button(seat_area, f"{row_number}F", row_number, 7, wide=True)

            elif seat_class == "Business Class":
                # 1 - 2 - 1: single seats by the windows, pair in the middle.
                self._create_seat_button(seat_area, f"{row_number}A", row_number, 1)
                tk.Label(seat_area, text=" ", bg="white", width=3).grid(row=row_number, column=2)
                self._create_seat_button(seat_area, f"{row_number}B", row_number, 3)
                self._create_seat_button(seat_area, f"{row_number}E", row_number, 4)
                tk.Label(seat_area, text=" ", bg="white", width=3).grid(row=row_number, column=5)
                self._create_seat_button(seat_area, f"{row_number}F", row_number, 7)

            else:
                # 3 - 3: standard economy layout.
                self._create_seat_button(seat_area, f"{row_number}A", row_number, 1)
                self._create_seat_button(seat_area, f"{row_number}B", row_number, 2)
                self._create_seat_button(seat_area, f"{row_number}C", row_number, 3)
                tk.Label(
                    seat_area, text="AISLE", bg="white", fg="#a0aab2",
                    font=("Segoe UI", 8, "bold"), width=7
                ).grid(row=row_number, column=4)
                self._create_seat_button(seat_area, f"{row_number}D", row_number, 5)
                self._create_seat_button(seat_area, f"{row_number}E", row_number, 6)
                self._create_seat_button(seat_area, f"{row_number}F", row_number, 7)

        # Rear of the aircraft
        tk.Label(
            aircraft, text="REAR  •  LAVATORY  •  GALLEY",
            bg="#dbeaf5", fg="#526575",
            font=("Segoe UI", 9, "bold"), pady=8
        ).pack(fill="x", padx=25, pady=(0, 12))

        # -------------------------------------------------------
        # Seat colour legend
        # -------------------------------------------------------
        legend_outer = tk.Frame(map_card, bg="white")
        legend_outer.pack(fill="x", padx=10, pady=(4, 12))
        self._legend(legend_outer, padx=5, pady=3)

        # -------------------------------------------------------
        # RIGHT: Selection summary
        # -------------------------------------------------------
        side = self.card(main, "Selection Summary")
        side.pack(side="right", fill="y", padx=(8, 0))

        available = 60 - len(self.booked_seats[f["code"]])
        tk.Label(
            side, text=f"Available seats: {available}/60",
            bg="white", fg="#2e7d32",
            font=("Segoe UI", 11, "bold")
        ).pack(padx=25, pady=(20, 5))

        self.selection_label = tk.Label(
            side, text="0 seat(s) selected", bg="white",
            fg="#173f5f", font=("Segoe UI", 14, "bold")
        )
        self.selection_label.pack(padx=25, pady=8)

        self.selected_seats_text = tk.Label(
            side, text="No seats selected", bg="white",
            fg="#667785", justify="left",
            font=("Segoe UI", 10), wraplength=220
        )
        self.selected_seats_text.pack(padx=25, pady=8)

        tk.Label(
            side,
            text=("Seat patterns\n"
                  "First:    [Seat]   aisle   [Seat]\n"
                  "Business: [Seat] [Seat][Seat] [Seat]\n"
                  "Economy:  [Seat][Seat][Seat] aisle [Seat][Seat][Seat]"),
            bg="white", fg="#667785", justify="left",
            font=("Segoe UI", 8)
        ).pack(padx=25, pady=15)

        ttk.Button(
            side, text="Continue to Passenger Details →",
            style="Primary.TButton", command=self.show_passenger_details
        ).pack(padx=25, pady=25)

    def _create_seat_button(self, parent, seat, row, col, wide=False):
        booked = self.booked_seats[self.selected_flight["code"]].get(seat)
        seat_class = SEAT_CLASS[seat]

        if booked:
            # Occupied seat color represents the gender of the passenger.
            bg = GENDER_COLORS.get(booked.gender, GENDER_COLORS["Other"])
            state = "disabled"
            command = None
        else:
            bg = {
                "First Class": "#f4d35e",
                "Business Class": "#8ecae6",
                "Economy Class": "#90be6d"
            }[seat_class]
            state = "normal"
            command = lambda s=seat: self.toggle_seat(s)

        button = tk.Button(
            parent, text=seat,
            width=8 if wide else 5,
            height=2 if wide else 1,
            bg=bg, fg="#173f5f",
            activebackground="#1769aa", activeforeground="white",
            bd=1, relief="solid",
            font=("Segoe UI", 8, "bold"),
            state=state, command=command,
            disabledforeground="#173f5f"
        )
        button.grid(row=row, column=col, padx=3, pady=3)
        self.seat_buttons[seat] = button

    def _legend(self, parent, padx=4, pady=2):
        items = [
            ("Available — First", "#f4d35e"),
            ("Available — Business", "#8ecae6"),
            ("Available — Economy", "#90be6d"),
            ("Selected", "#1769aa"),
            ("Female booked", GENDER_COLORS["Female"]),
            ("Male booked", GENDER_COLORS["Male"]),
            ("Other booked", GENDER_COLORS["Other"])
        ]
        for text, color in items:
            item = tk.Frame(parent, bg="white")
            item.pack(side="left", padx=padx, pady=pady)
            tk.Label(item, text="  ", bg=color, relief="solid", bd=1).pack(side="left", padx=(0, 3))
            tk.Label(item, text=text, bg="white", fg="#667785", font=("Segoe UI", 7)).pack(side="left")

    def toggle_seat(self, seat):
        if seat in self.selected_seats:
            self.selected_seats.remove(seat)
        else:
            self.selected_seats.append(seat)

        self.selected_seats.sort(key=lambda s: (int(s[:-1]), s[-1]))
        self._refresh_selected_seats()

    def _refresh_selected_seats(self):
        for seat, button in self.seat_buttons.items():
            if seat in self.selected_seats:
                button.configure(bg="#1769aa", fg="white")
            elif seat not in self.booked_seats[self.selected_flight["code"]]:
                button.configure(
                    bg={
                        "First Class": "#f4d35e",
                        "Business Class": "#8ecae6",
                        "Economy Class": "#90be6d"
                    }[SEAT_CLASS[seat]],
                    fg="#173f5f"
                )

        self.selection_label.configure(
            text=f"{len(self.selected_seats)} seat(s) selected"
        )

        if self.selected_seats:
            self.selected_seats_text.configure(
                text="\n".join(
                    f"• {seat} — {SEAT_CLASS[seat]}"
                    for seat in self.selected_seats
                )
            )
        else:
            self.selected_seats_text.configure(
                text="No seats selected"
            )

    def show_passenger_details(self):
        if not self.selected_seats:
            messagebox.showwarning("Select Seats", "Please select at least one available seat.")
            return
        self.clear_content()
        f = self.selected_flight
        self.page_title("3. Passenger Details", f"Enter details for each selected seat on {f['code']}.")
        outer = tk.Frame(self.content, bg="#eef3f8")
        outer.pack(fill="both", expand=True, padx=25)
        canvas = tk.Canvas(outer, bg="#eef3f8", highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        form = tk.Frame(canvas, bg="#eef3f8")
        form.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form, anchor="nw", width=900)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.passenger_entries = {}
        for index, seat in enumerate(self.selected_seats, start=1):
            c = self.card(form, f"Passenger {index}  •  Seat {seat}  •  {SEAT_CLASS[seat]}")
            c.pack(fill="x", pady=6)
            grid = tk.Frame(c, bg="white")
            grid.pack(fill="x", padx=18, pady=(0, 15))
            entries = {}
            fields = [("Passenger ID", "id"), ("Name", "name"), ("Age", "age"), ("Gender", "gender"), ("Phone", "phone"), ("Email", "email")]
            for i, (label, key) in enumerate(fields):
                r, col = divmod(i, 2)
                tk.Label(grid, text=label, bg="white", fg="#455a64", font=("Segoe UI", 9, "bold")).grid(row=r*2, column=col, sticky="w", padx=8, pady=(7, 2))
                if key == "gender":
                    w = ttk.Combobox(grid, values=["Female", "Male", "Other"], state="readonly", width=35)
                    w.set("Female")
                elif key == "id":
                    w = tk.Entry(grid, width=38)
                    self.passenger_counter += 1
                    w.insert(0, f"P{self.passenger_counter}")
                else:
                    w = tk.Entry(grid, width=38)
                w.grid(row=r*2+1, column=col, sticky="w", padx=8, pady=(0, 5))
                entries[key] = w
            self.passenger_entries[seat] = entries
        bottom = tk.Frame(self.content, bg="#eef3f8")
        bottom.pack(fill="x", padx=25, pady=12)
        ttk.Button(bottom, text="← Back to Seats", command=self.show_seat_selection).pack(side="left")
        ttk.Button(bottom, text="Add to Booking Queue →", style="Primary.TButton",
                   command=self.add_to_queue).pack(side="right")

    def _entry_value(self, widget):
        return widget.get().strip()

    def add_to_queue(self):
        passengers = []
        for seat in self.selected_seats:
            e = self.passenger_entries[seat]
            pid = self._entry_value(e["id"])
            name = self._entry_value(e["name"])
            age_text = self._entry_value(e["age"])
            gender = e["gender"].get().strip()
            phone = self._entry_value(e["phone"])
            email = self._entry_value(e["email"])
            if not all([pid, name, age_text, gender, phone, email]):
                messagebox.showerror("Missing Details", f"Please complete all fields for seat {seat}.")
                return
            if not age_text.isdigit() or not 1 <= int(age_text) <= 120:
                messagebox.showerror("Invalid Age", f"Enter a valid age for seat {seat}.")
                return
            if not phone.isdigit() or len(phone) != 10:
                messagebox.showerror("Invalid Phone", f"Phone number for seat {seat} must contain exactly 10 digits.")
                return
            if "@" not in email or "." not in email.split("@")[-1]:
                messagebox.showerror("Invalid Email", f"Enter a valid email for seat {seat}.")
                return
            if self.bst.search(pid) is not None:
                messagebox.showerror("Duplicate Passenger ID", f"Passenger ID {pid} already exists in confirmed bookings.")
                return
            # Also prevent duplicate IDs within the current request.
            if any(p.passenger_id == pid for p in passengers):
                messagebox.showerror("Duplicate Passenger ID", f"Passenger ID {pid} is repeated in this booking.")
                return
            fare = self.selected_flight["price"] * CLASS_PRICES[SEAT_CLASS[seat]]
            passengers.append(Passenger(pid, name, int(age_text), gender, phone, email,
                                        self.selected_flight["code"], seat, SEAT_CLASS[seat], fare, ""))
        request = BookingRequest(passengers, datetime.now().strftime("%d-%b-%Y %I:%M %p"))
        self.queue.enqueue(request)
        self.history.append({
            "timestamp": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
            "action": "QUEUED",
            "booking_id": "Pending",
            "passengers": len(passengers),
            "passenger_name": ", ".join(p.name for p in passengers),
            "flight_code": self.selected_flight["code"],
            "seats": ", ".join(p.seat for p in passengers)
        })
        self._save_data()
        self.header_status.configure(text=f"Queue: {self.queue.size()} pending")
        messagebox.showinfo("Added to Queue", f"{len(passengers)} passenger(s) added as one FIFO booking request.\n\nUse Booking Queue to process the request and confirm the seats.")
        self.show_queue()

    # ------------------------ QUEUE ---------------------------
    def show_queue(self):
        self.clear_content()
        self.page_title("4. Booking Queue", "Requests are processed in First-In-First-Out (FIFO) order.")
        c = self.card(self.content, "Pending Requests")
        c.pack(fill="both", expand=True, padx=25, pady=5)
        if not self.queue.items:
            tk.Label(c, text="No pending booking requests.", bg="white", fg="#667785",
                     font=("Segoe UI", 12)).pack(pady=80)
        else:
            columns = ("position", "passengers", "flight", "seats", "requested")
            tree = ttk.Treeview(c, columns=columns, show="headings", height=13)
            headings = {"position":"Queue #", "passengers":"Passengers", "flight":"Flight", "seats":"Seats", "requested":"Requested At"}
            for col in columns:
                tree.heading(col, text=headings[col])
                tree.column(col, anchor="center", width=150)
            tree.column("requested", width=210)
            for i, req in enumerate(self.queue.items, start=1):
                tree.insert("", "end", values=(i, len(req.passengers), req.passengers[0].flight_code,
                                                  ", ".join(p.seat for p in req.passengers), req.requested_at))
            tree.pack(fill="both", expand=True, padx=18, pady=12)
            ttk.Button(c, text="Process Next Request (FIFO) →", style="Primary.TButton",
                       command=self.process_next_request).pack(pady=(0, 15))

    def process_next_request(self):
        request = self.queue.peek()
        if request is None:
            messagebox.showinfo("Queue Empty", "There are no pending requests.")
            return
        flight_code = request.passengers[0].flight_code
        # Verify seats have not become unavailable before confirmation.
        for p in request.passengers:
            if p.seat in self.booked_seats[flight_code]:
                messagebox.showerror("Seat Conflict", f"Seat {p.seat} is already booked. The request was not processed.")
                return
        request = self.queue.dequeue()
        self.booking_counter += 1
        booking_id = f"BK{self.booking_counter}"
        for p in request.passengers:
            p.booking_id = booking_id
            self.booked_seats[p.flight_code][p.seat] = p
            self.bst.insert(p.passenger_id, p)
        self.history.append({
            "timestamp": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
            "action": "CONFIRMED",
            "booking_id": booking_id,
            "passengers": len(request.passengers),
            "passenger_name": ", ".join(p.name for p in request.passengers),
            "flight_code": flight_code,
            "seats": ", ".join(p.seat for p in request.passengers)
        })
        self._save_data()
        self.header_status.configure(text=f"Confirmed: {booking_id}")
        names = ", ".join(p.name for p in request.passengers)
        total = sum(p.fare for p in request.passengers)
        messagebox.showinfo("Booking Confirmed", f"Booking ID: {booking_id}\nPassengers: {names}\nTotal Fare: ₹{total:,.2f}\n\nSeats: {', '.join(p.seat for p in request.passengers)}")
        self.show_queue()

    # ------------------------- SEARCH -------------------------
    def show_search(self):
        self.clear_content()
        self.page_title("5. Search Booking", "BST search retrieves a confirmed passenger record using Passenger ID.")
        c = self.card(self.content, "Binary Search Tree Search")
        c.pack(fill="x", padx=25, pady=5)
        row = tk.Frame(c, bg="white")
        row.pack(padx=20, pady=20)
        tk.Label(row, text="Passenger ID", bg="white", fg="#455a64", font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)
        entry = tk.Entry(row, width=30, font=("Segoe UI", 10))
        entry.pack(side="left", padx=8)
        result = tk.Frame(self.content, bg="white", highlightbackground="#d9e2ea", highlightthickness=1)
        result.pack(fill="both", expand=True, padx=25, pady=12)
        tk.Label(result, text="Enter a Passenger ID and click Search.", bg="white", fg="#667785",
                 font=("Segoe UI", 11)).pack(pady=60)
        def search():
            for child in result.winfo_children():
                child.destroy()
            pid = entry.get().strip()
            if not pid:
                messagebox.showwarning("Input", "Enter a Passenger ID.")
                return
            p = self.bst.search(pid)
            if not p:
                tk.Label(result, text="Passenger record not found in BST.", bg="white", fg="#c62828",
                         font=("Segoe UI", 12, "bold")).pack(pady=60)
                return
            details = [
                ("Booking ID", p.booking_id), ("Passenger ID", p.passenger_id), ("Name", p.name),
                ("Age", p.age), ("Gender", p.gender), ("Phone", p.phone), ("Email", p.email),
                ("Flight", p.flight_code), ("Seat", p.seat), ("Class", p.seat_class), ("Fare", f"₹{p.fare:,.2f}")
            ]
            tk.Label(result, text="Passenger Found", bg="white", fg="#2e7d32",
                     font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=25, pady=(20, 10))
            grid = tk.Frame(result, bg="white")
            grid.pack(anchor="w", padx=25)
            for i, (label, value) in enumerate(details):
                r, col = divmod(i, 2)
                tk.Label(grid, text=label+":", bg="white", fg="#667785", font=("Segoe UI", 9, "bold"), width=18, anchor="w").grid(row=r, column=col*2, padx=5, pady=7)
                tk.Label(grid, text=str(value), bg="white", fg="#173f5f", font=("Segoe UI", 10), width=28, anchor="w").grid(row=r, column=col*2+1, padx=5, pady=7)
        ttk.Button(row, text="Search", style="Primary.TButton", command=search).pack(side="left", padx=10)
        entry.bind("<Return>", lambda e: search())

    # ----------------------- CANCELLATION ---------------------
    def show_cancel(self):
        self.clear_content()
        self.page_title("6. Cancellation", "Cancel a confirmed passenger record using the BST and release the seat.")
        c = self.card(self.content, "Cancel by Passenger ID")
        c.pack(fill="x", padx=25, pady=5)
        row = tk.Frame(c, bg="white")
        row.pack(padx=20, pady=20)
        tk.Label(row, text="Passenger ID", bg="white", fg="#455a64", font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)
        entry = tk.Entry(row, width=30)
        entry.pack(side="left", padx=8)
        def cancel():
            pid = entry.get().strip()
            if not pid:
                messagebox.showwarning("Input", "Enter a Passenger ID.")
                return
            p = self.bst.search(pid)
            if not p:
                messagebox.showerror("Not Found", "Passenger ID was not found in confirmed bookings.")
                return
            ok = messagebox.askyesno("Confirm Cancellation", f"Cancel booking record for {p.name} ({p.passenger_id})?\nSeat {p.seat} will be released.")
            if not ok:
                return
            self.bst.delete(pid)
            self.booked_seats[p.flight_code].pop(p.seat, None)
            self.history.append({
                "timestamp": datetime.now().strftime("%d-%b-%Y %I:%M %p"),
                "action": "CANCELLED",
                "booking_id": p.booking_id,
                "passengers": 1,
                "passenger_name": p.name,
                "flight_code": p.flight_code,
                "seats": p.seat
            })
            self._save_data()
            messagebox.showinfo("Cancelled", f"Passenger {p.name} cancelled successfully.\nSeat {p.seat} is now available.")
            self.show_cancel()
        ttk.Button(row, text="Cancel Booking", style="Primary.TButton", command=cancel).pack(side="left", padx=10)

        note = tk.Frame(self.content, bg="#fff8e1", highlightbackground="#f0d27a", highlightthickness=1)
        note.pack(fill="x", padx=25, pady=15)
        tk.Label(note, text="Note: For a group booking, cancel each Passenger ID separately so every passenger record can be removed from the BST and each seat can be released.",
                 bg="#fff8e1", fg="#6d5700", font=("Segoe UI", 9), wraplength=850, justify="left").pack(padx=15, pady=12)

    # ---------------------- HISTORY ---------------------------
    def show_history(self):
        self.clear_content()
        self.page_title(
            "Booking History",
            "Persistent history loaded from the local JSON file: airline_reservation_data.json"
        )
        c = self.card(self.content, "Reservation Activity")
        c.pack(fill="both", expand=True, padx=25, pady=5)

        columns = ("time", "action", "booking", "passenger", "flight", "seats")
        tree = ttk.Treeview(c, columns=columns, show="headings")
        headings = {
            "time": "Timestamp", "action": "Action", "booking": "Booking ID",
            "passenger": "Passenger(s)", "flight": "Flight", "seats": "Seat(s)"
        }
        widths = {"time": 175, "action": 100, "booking": 100, "passenger": 240, "flight": 80, "seats": 160}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center")
        for item in reversed(self.history):
            tree.insert("", "end", values=(
                item.get("timestamp", ""), item.get("action", ""), item.get("booking_id", ""),
                item.get("passenger_name", ""), item.get("flight_code", ""), item.get("seats", "")
            ))
        tree.pack(fill="both", expand=True, padx=15, pady=15)

        footer = tk.Frame(c, bg="white")
        footer.pack(fill="x", padx=20, pady=(0, 14))
        tk.Label(
            footer,
            text=f"History entries: {len(self.history)}   •   Data file: {self.data_file.name}",
            bg="white", fg="#667785", font=("Segoe UI", 9, "bold")
        ).pack(side="left")
        ttk.Button(footer, text="Save Now", command=self._save_data).pack(side="right")

    # ---------------------- CONFIRMED -------------------------
    def show_confirmed(self):
        self.clear_content()
        self.page_title("7. Confirmed Bookings", "Inorder traversal of the BST displays passenger records sorted by Passenger ID.")
        c = self.card(self.content, "Confirmed Passenger Records — BST Inorder Traversal")
        c.pack(fill="both", expand=True, padx=25, pady=5)
        columns = ("pid", "booking", "name", "flight", "seat", "class", "gender", "fare")
        tree = ttk.Treeview(c, columns=columns, show="headings")
        headings = {"pid":"Passenger ID", "booking":"Booking ID", "name":"Name", "flight":"Flight", "seat":"Seat", "class":"Class", "gender":"Gender", "fare":"Fare"}
        widths = {"pid":110,"booking":100,"name":150,"flight":80,"seat":60,"class":120,"gender":80,"fare":100}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center")
        for p in self.bst.inorder():
            tree.insert("", "end", values=(p.passenger_id, p.booking_id, p.name, p.flight_code, p.seat, p.seat_class, p.gender, f"₹{p.fare:,.0f}"))
        tree.pack(fill="both", expand=True, padx=15, pady=15)
        tk.Label(c, text=f"BST records: {len(self.bst.inorder())}", bg="white", fg="#667785",
                 font=("Segoe UI", 9, "bold")).pack(anchor="e", padx=20, pady=(0, 12))

if __name__ == "__main__":
    app = AirlineApp()
    app.mainloop()
