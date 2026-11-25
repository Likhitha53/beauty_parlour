
import streamlit as st
import requests
import pandas as pd
import os
from datetime import date, time

st.set_page_config(
    page_title="Glow Beauty Parlour",
    page_icon="💇‍♀️",
    layout="wide"
)

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
).rstrip("/")

# CUSTOM CSS
st.markdown("""
<style>
.stApp {
    background-color: #fff7f7;
}

h1, h2, h3 {
    color: #803f5b;
}

div.stButton > button {
    background-color: #a65c79;
    color: white;
    border-radius: 8px;
    border: none;
}

[data-testid="stSidebar"] {
    background-color: #f5e3e9;
}
</style>
""", unsafe_allow_html=True)


# API FUNCTION
def api_request(method, endpoint, **kwargs):
    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            timeout=10,
            **kwargs
        )

        if response.ok:
            return response.json(), None

        try:
            error = response.json().get("detail", response.text)
        except ValueError:
            error = response.text

        return None, error

    except requests.RequestException as e:
        return None, str(e)


# NAVIGATION
st.title("💇‍♀️ Glow Beauty Parlour")
st.write("Beauty, Care and Confidence!")

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Our Services",
        "Book Appointment",
        "Manage Appointments"
    ]
)


# HOME PAGE
if page == "Home":

    st.header("Welcome to Glow Beauty Parlour")

    st.write(
        "Your destination for beauty and personal care."
    )

    services, error = api_request("GET", "/services")
    appointments, appt_error = api_request("GET", "/appointments")

    if error:
        st.error(error)
    else:
        col1, col2 = st.columns(2)

        col1.metric(
            "Available Services",
            len(services)
        )

        if appt_error:
            col2.metric("Appointments", "—")
        else:
            col2.metric(
                "Total Appointments",
                len(appointments)
            )

    st.info("Select an option from the sidebar.")


# SERVICES PAGE
elif page == "Our Services":

    st.header("Our Beauty Services")

    data, error = api_request("GET", "/services")

    if error:
        st.error(error)

    else:
        cols = st.columns(2)

        for i, service in enumerate(data):

            with cols[i % 2]:

                with st.container(border=True):

                    st.subheader(service["name"])

                    st.write(service["description"])

                    st.write(
                        f"Price: ₹{service['price']}"
                    )

                    st.write(
                        f"Duration: {service['duration_minutes']} minutes"
                    )


# BOOK APPOINTMENT
elif page == "Book Appointment":

    st.header("Book Your Appointment")

    services, error = api_request("GET", "/services")

    if error:
        st.error(error)

    elif services:

        service_options = {
            f"{s['name']} - ₹{s['price']}": s["id"]
            for s in services
        }

        with st.form("appointment_form"):

            name = st.text_input("Customer Name")

            phone = st.text_input("Phone Number")

            selected_service = st.selectbox(
                "Select Service",
                list(service_options.keys())
            )

            appointment_date = st.date_input(
                "Appointment Date",
                min_value=date.today()
            )

            appointment_time = st.time_input(
                "Appointment Time",
                value=time(10, 0)
            )

            submit = st.form_submit_button(
                "Book Appointment"
            )

        if submit:

            if not name.strip() or not phone.strip():
                st.warning("Please enter all details.")

            else:

                payload = {
                    "customer_name": name.strip(),
                    "phone": phone.strip(),
                    "service_id": service_options[selected_service],
                    "appointment_date": appointment_date.isoformat(),
                    "appointment_time": appointment_time.isoformat()
                }

                result, error = api_request(
                    "POST",
                    "/appointments",
                    json=payload
                )

                if error:
                    st.error(error)

                else:
                    st.success("Appointment booked successfully!")

                    st.json(result)


# MANAGE APPOINTMENTS
elif page == "Manage Appointments":

    st.header("Manage Appointments")

    data, error = api_request(
        "GET",
        "/appointments"
    )

    if error:
        st.error(error)

    elif not data:

        st.info("No appointments available.")

    else:

        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("Update Appointment Status")

        ids = [item["id"] for item in data]

        selected_id = st.selectbox(
            "Select Appointment ID",
            ids
        )

        status = st.selectbox(
            "Select New Status",
            ["Booked", "Completed", "Cancelled"]
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button("Update Status"):

                result, error = api_request(
                    "PATCH",
                    f"/appointments/{selected_id}/status",
                    params={"new_status": status}
                )

                if error:
                    st.error(error)

                else:
                    st.success("Status updated successfully!")
                    st.rerun()

        with col2:

            if st.button("Delete Appointment"):

                result, error = api_request(
                    "DELETE",
                    f"/appointments/{selected_id}"
                )

                if error:
                    st.error(error)

                else:
                    st.success("Appointment deleted!")
                    st.rerun()
