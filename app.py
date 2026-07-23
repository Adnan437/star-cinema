"""
Star Cinema - Web App (Streamlit)
A polished, web-based version of the console cinema seat-booking system.

Run locally with:
    python -m streamlit run app.py
"""

import streamlit as st

# ---------------------------------------------------------------------------
# CORE LOGIC (same OOP structure as the original console project)
# ---------------------------------------------------------------------------

class StarCinema:
    hall_list = []  # class attribute shared by all Hall objects

    def entry_hall(self, hall_no):
        StarCinema.hall_list.append(hall_no)


class Hall(StarCinema):
    def __init__(self, rows, cols, hall_no):
        self.seats = {}        # show_id -> 2D list of True(free)/False(booked)
        self.show_list = []    # list of (show_id, movie_name, time, color)
        self.rows = rows
        self.cols = cols
        self.hall_no = hall_no
        self.entry_hall(hall_no)

    def entry_show(self, show_id, movie_name, time, poster_color="#333"):
        if any(s[0] == show_id for s in self.show_list):
            return False
        self.show_list.append((show_id, movie_name, time, poster_color))
        self.seats[show_id] = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        return True

    def get_show(self, show_id):
        for s in self.show_list:
            if s[0] == show_id:
                return s
        return None

    def book_seats(self, customer_name, phone, show_id, seat_list):
        show = self.get_show(show_id)
        if not show:
            return False, "Invalid show ID."
        if not seat_list:
            return False, "No seats selected."

        for r, c in seat_list:
            if r < 0 or c < 0 or r >= self.rows or c >= self.cols:
                return False, "Invalid seat number."
            if not self.seats[show_id][r][c]:
                return False, f"Seat {chr(65 + r)}{c} is already booked."

        for r, c in seat_list:
            self.seats[show_id][r][c] = False

        return True, f"Booked {len(seat_list)} seat(s) for {customer_name}."


# ---------------------------------------------------------------------------
# PAGE CONFIG + CUSTOM STYLING
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Star Cinema", page_icon="\U0001F3AC", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(180deg, #0E1117 0%, #14161c 100%); }

    .cinema-header {
        text-align: center;
        padding: 1.6rem 0 1rem 0;
    }
    .cinema-header h1 {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: 2px;
        background: linear-gradient(90deg, #E50914, #ff6a6a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .cinema-header p {
        color: #9aa0a6;
        font-size: 0.95rem;
        margin-top: 0.2rem;
    }

    .movie-card {
        border-radius: 14px;
        padding: 1.1rem 1.2rem;
        margin-bottom: 0.9rem;
        color: white;
        box-shadow: 0 4px 14px rgba(0,0,0,0.35);
    }
    .movie-card h3 { margin: 0 0 0.3rem 0; }
    .movie-card .meta { opacity: 0.85; font-size: 0.9rem; }

    .screen-bar {
        width: 100%;
        height: 10px;
        background: linear-gradient(90deg, transparent, #E50914, transparent);
        border-radius: 50%;
        margin: 0.5rem 0 1.4rem 0;
        opacity: 0.8;
    }
    .screen-label {
        text-align: center;
        color: #9aa0a6;
        letter-spacing: 6px;
        font-size: 0.75rem;
        margin-bottom: 0.2rem;
    }

    .legend-box {
        display: inline-block;
        width: 14px; height: 14px;
        border-radius: 3px;
        margin-right: 6px;
        vertical-align: middle;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def init_state():
    if "hall" not in st.session_state:
        hall = Hall(rows=5, cols=8, hall_no="Hall 1")
        hall.entry_show("abc", "Finding Nemo", "03:50 PM", "#1f6fb2")
        hall.entry_show("asd", "Ice Age", "10:00 AM", "#2a9d8f")
        hall.entry_show("bcd", "Avatar", "05:00 PM", "#6a4c93")
        st.session_state.hall = hall
    if "selected_seats" not in st.session_state:
        st.session_state.selected_seats = set()
    if "last_show" not in st.session_state:
        st.session_state.last_show = None


init_state()
hall = st.session_state.hall

# ---------------------------------------------------------------------------
# HEADER
# ---------------------------------------------------------------------------
st.markdown(f"""
<div class="cinema-header">
    <h1>\U0001F3AC STAR CINEMA</h1>
    <p>{hall.hall_no} &nbsp;•&nbsp; {hall.rows} rows &times; {hall.cols} seats/row &nbsp;•&nbsp; Book your show in seconds</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### \U0001F39F\uFE0F Navigate")
    page = st.radio("Menu", ["\U0001F3A5 Now Showing", "\U0001F39F\uFE0F Book Tickets", "\u2795 Add a Show"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("Built with Python + Streamlit")

# ---------------------------------------------------------------------------
# PAGE: Now Showing
# ---------------------------------------------------------------------------
if page.endswith("Now Showing"):
    st.subheader("Now Showing")
    if not hall.show_list:
        st.info("No shows added yet.")
    else:
        cols = st.columns(min(3, len(hall.show_list)))
        for i, (show_id, name, time, color) in enumerate(hall.show_list):
            free = sum(row.count(True) for row in hall.seats[show_id])
            total = hall.rows * hall.cols
            pct = free / total
            with cols[i % len(cols)]:
                st.markdown(f"""
                <div class="movie-card" style="background:{color};">
                    <h3>{name}</h3>
                    <div class="meta">\U0001F3AB Show ID: {show_id}</div>
                    <div class="meta">\U0001F550 {time}</div>
                    <div class="meta">\U0001F4BA {free}/{total} seats free</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(pct)

# ---------------------------------------------------------------------------
# PAGE: Book Tickets
# ---------------------------------------------------------------------------
elif page.endswith("Book Tickets"):
    st.subheader("Book Tickets")

    if not hall.show_list:
        st.info("No shows available yet. Add one from 'Add a Show'.")
    else:
        show_options = {f"{name}  —  {time}  ({sid})": sid for sid, name, time, _ in hall.show_list}
        chosen_label = st.selectbox("Choose a show", list(show_options.keys()))
        show_id = show_options[chosen_label]

        if st.session_state.last_show != show_id:
            st.session_state.selected_seats = set()
            st.session_state.last_show = show_id

        st.markdown('<div class="screen-label">S C R E E N</div>', unsafe_allow_html=True)
        st.markdown('<div class="screen-bar"></div>', unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.markdown('<span class="legend-box" style="background:#2a2f3a;border:1px solid #555;"></span> Available', unsafe_allow_html=True)
        c2.markdown('<span class="legend-box" style="background:#E50914;"></span> Selected', unsafe_allow_html=True)
        c3.markdown('<span class="legend-box" style="background:#444;"></span> Booked', unsafe_allow_html=True)
        st.write("")

        grid = hall.seats[show_id]
        for r in range(hall.rows):
            row_cols = st.columns([0.4] + [1] * hall.cols)
            row_cols[0].markdown(f"**{chr(65 + r)}**")
            for c in range(hall.cols):
                seat_label = f"{chr(65 + r)}{c}"
                is_booked = not grid[r][c]
                is_selected = (r, c) in st.session_state.selected_seats

                if is_booked:
                    row_cols[c + 1].button("✕", key=f"seat_{r}_{c}", disabled=True, use_container_width=True)
                else:
                    btn_label = "●" if is_selected else str(c)
                    if row_cols[c + 1].button(btn_label, key=f"seat_{r}_{c}", use_container_width=True):
                        if is_selected:
                            st.session_state.selected_seats.discard((r, c))
                        else:
                            st.session_state.selected_seats.add((r, c))
                        st.rerun()

        st.markdown("---")
        selected = sorted(st.session_state.selected_seats)
        seat_names = ", ".join(f"{chr(65 + r)}{c}" for r, c in selected) or "None"
        st.markdown(f"**Selected seats:** {seat_names}  &nbsp;|&nbsp;  **Total:** {len(selected)} seat(s)")

        with st.form("booking_form"):
            fc1, fc2 = st.columns(2)
            name = fc1.text_input("Your name")
            phone = fc2.text_input("Phone number")
            submitted = st.form_submit_button("\U0001F39F\uFE0F Confirm Booking", use_container_width=True)

            if submitted:
                if not name or not phone:
                    st.error("Please enter your name and phone number.")
                else:
                    ok, msg = hall.book_seats(name, phone, show_id, selected)
                    if ok:
                        st.success(msg)
                        st.balloons()
                        st.session_state.selected_seats = set()
                        st.rerun()
                    else:
                        st.error(msg)

# ---------------------------------------------------------------------------
# PAGE: Add a Show
# ---------------------------------------------------------------------------
elif page.endswith("Add a Show"):
    st.subheader("Add a New Show")
    with st.form("add_show_form"):
        show_id = st.text_input("Show ID (unique, e.g. xyz)")
        movie_name = st.text_input("Movie name")
        time = st.text_input("Show time (e.g. 07:00 PM)")
        color = st.color_picker("Card color", "#1f6fb2")
        submitted = st.form_submit_button("Add Show", use_container_width=True)

        if submitted:
            if not show_id or not movie_name or not time:
                st.error("Please fill in all fields.")
            else:
                added = hall.entry_show(show_id, movie_name, time, color)
                if added:
                    st.success(f"Added show '{movie_name}' with ID '{show_id}'.")
                else:
                    st.error("A show with that ID already exists. Choose a different ID.")
