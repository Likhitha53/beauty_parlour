
from datetime import date, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Glow Beauty Parlour API",
    description="Beauty Parlour Management System",
    version="1.0.0"
)

# Service Model
class Service(BaseModel):
    id: int
    name: str
    description: str
    price: float
    duration_minutes: int


# Appointment Model
class AppointmentCreate(BaseModel):
    customer_name: str = Field(min_length=2)
    phone: str = Field(min_length=10, max_length=15)
    service_id: int
    appointment_date: date
    appointment_time: time


class Appointment(AppointmentCreate):
    id: int
    status: str = "Booked"


# Available Services
services = {
    1: Service(
        id=1,
        name="Haircut",
        description="Hair trimming and styling",
        price=300,
        duration_minutes=30
    ),
    2: Service(
        id=2,
        name="Facial",
        description="Refreshing facial treatment",
        price=800,
        duration_minutes=60
    ),
    3: Service(
        id=3,
        name="Manicure",
        description="Nail cleaning and polish",
        price=400,
        duration_minutes=40
    ),
    4: Service(
        id=4,
        name="Bridal Makeup",
        description="Professional bridal makeup",
        price=5000,
        duration_minutes=180
    ),
    5: Service(
        id=5,
        name="Hair Spa",
        description="Nourishing hair spa treatment",
        price=1200,
        duration_minutes=75
    )
}

appointments = {}
next_id = 1


# HOME
@app.get("/")
def home():
    return {
        "message": "Welcome to Glow Beauty Parlour",
        "documentation": "/docs"
    }


# GET ALL SERVICES
@app.get("/services")
def get_services():
    return list(services.values())


# GET SINGLE SERVICE
@app.get("/services/{service_id}")
def get_service(service_id: int):
    if service_id not in services:
        raise HTTPException(404, "Service not found")

    return services[service_id]


# POST - BOOK APPOINTMENT
@app.post("/appointments")
def create_appointment(data: AppointmentCreate):
    global next_id

    if data.service_id not in services:
        raise HTTPException(404, "Service not found")

    if data.appointment_date < date.today():
        raise HTTPException(400, "Invalid appointment date")

    appointment = Appointment(
        id=next_id,
        **data.model_dump()
    )

    appointments[next_id] = appointment
    next_id += 1

    return appointment


# GET ALL APPOINTMENTS
@app.get("/appointments")
def get_appointments():
    return list(appointments.values())


# GET SINGLE APPOINTMENT
@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: int):
    if appointment_id not in appointments:
        raise HTTPException(404, "Appointment not found")

    return appointments[appointment_id]


# PUT - UPDATE APPOINTMENT
@app.put("/appointments/{appointment_id}")
def update_appointment(
    appointment_id: int,
    data: AppointmentCreate
):
    if appointment_id not in appointments:
        raise HTTPException(404, "Appointment not found")

    if data.service_id not in services:
        raise HTTPException(404, "Service not found")

    if data.appointment_date < date.today():
        raise HTTPException(400, "Invalid appointment date")

    updated = Appointment(
        id=appointment_id,
        **data.model_dump(),
        status="Updated"
    )

    appointments[appointment_id] = updated

    return updated


# PATCH - UPDATE STATUS
@app.patch("/appointments/{appointment_id}/status")
def update_status(appointment_id: int, new_status: str):

    if appointment_id not in appointments:
        raise HTTPException(404, "Appointment not found")

    if new_status not in ["Booked", "Completed", "Cancelled"]:
        raise HTTPException(400, "Invalid status")

    old = appointments[appointment_id]

    updated = old.model_copy(
        update={"status": new_status}
    )

    appointments[appointment_id] = updated

    return updated


# DELETE APPOINTMENT
@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int):

    if appointment_id not in appointments:
        raise HTTPException(404, "Appointment not found")

    del appointments[appointment_id]

    return {
        "message": "Appointment deleted successfully"
    }
