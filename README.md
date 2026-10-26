SkyReserve — Airline Seat Reservation System
SkyReserve is a Python desktop application that demonstrates how data structures and algorithms can support an airline seat reservation workflow. The interface is built with Tkinter/ttk, and booking history is stored locally in JSON.
Features
- Browse 10 predefined demonstration flights.
- View an aircraft-style seating layout with 60 seats per flight across First, Business, and Economy classes.
- Select seats and make single-passenger or group bookings.
- Validate passenger details and calculate fares by cabin class.
- Process booking requests in First In, First Out (FIFO) order using a queue.
- Sort sample flight fares using Selection Sort.
- Search, traverse, insert, and delete passenger records using a Binary Search Tree (BST).
- Cancel bookings and save booking history locally between sessions.
Note: The flight records are predefined demonstration data, not live airline schedules. The application creates airline_reservation_data.json in the same folder when it saves local booking data.

Requirements
- Python 3.10 or later recommended
- Tkinter (usually included with standard Python installations on Windows)
No third-party Python packages are required by the application.
How to run
1. Install Python from python.org if it is not already installed.
2. Download or clone this repository.
3. Open a terminal or command prompt in the project folder.
4. Run:
   
   python airline_seat_reservation_system.py
   
   On some Windows setups, use py airline_seat_reservation_system.py instead.
Core DSA concepts
- Queue (FIFO): processes booking requests in arrival order.
- Selection Sort: sorts predefined flights by base fare.
- Binary Search Tree: organises passenger records by passenger ID for searching and deletion.
Project purpose
This is an academic Data Structures and Algorithms micro-project for demonstrating the use of core DSA concepts in an interactive desktop application.
