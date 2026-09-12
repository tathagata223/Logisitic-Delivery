from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

vehicles = [
    {
        "id": "V001",
        "type": "Truck",
        "number": "WB01AB1234",
        "driver": "Rahul"
    },
    {
        "id": "V002",
        "type": "Van",
        "number": "WB02CD5678",
        "driver": "Amit"
    },
    {
        "id": "V003",
        "type": "Truck",
        "number": "WB03EF9012",
        "driver": "Suman"
    }
]

deliveries = []


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():

    search = request.args.get("search", "").strip().lower()
    status = request.args.get("status", "").strip()

    vehicle_search = request.args.get(
        "vehicle_search", ""
    ).strip().lower()

    delivery_list = []

    for d in deliveries:

        if search:
            if (
                search not in d["id"].lower()
                and search not in d["customer"].lower()
            ):
                continue

        if status and d["status"] != status:
            continue

        delivery_list.append(d)

    vehicle_list = []

    for v in vehicles:

        if vehicle_search:
            if (
                vehicle_search not in v["id"].lower()
                and vehicle_search not in v["number"].lower()
            ):
                continue

        vehicle_list.append(v)

    total = len(deliveries)

    pending = 0
    assigned = 0
    in_transit = 0
    delivered = 0
    cancelled = 0

    for d in deliveries:

        if d["status"] == "Pending":
            pending += 1

        elif d["status"] == "Assigned":
            assigned += 1

        elif d["status"] == "In Transit":
            in_transit += 1

        elif d["status"] == "Delivered":
            delivered += 1

        elif d["status"] == "Cancelled":
            cancelled += 1

    assigned_vehicle_ids = set()

    for d in deliveries:

        if d["status"] in ["Assigned", "In Transit"]:
            assigned_vehicle_ids.add(d["vehicle"])

    assigned_vehicles = len(assigned_vehicle_ids)
    available_vehicles = len(vehicles) - assigned_vehicles

    if total > 0:
        completion = round((delivered / total) * 100, 1)
    else:
        completion = 0

    error = request.args.get("error", "")
    success = request.args.get("success", "")

    return render_template(
        "dashboard.html",
        deliveries=delivery_list,
        vehicles=vehicle_list,
        total=total,
        pending=pending,
        assigned=assigned,
        in_transit=in_transit,
        delivered=delivered,
        cancelled=cancelled,
        assigned_vehicles=assigned_vehicles,
        available_vehicles=available_vehicles,
        completion=completion,
        search=search,
        status=status,
        vehicle_search=vehicle_search,
        error=error,
        success=success
    )


@app.route("/add_delivery", methods=["POST"])
def add_delivery():

    delivery_id = request.form.get(
        "delivery_id", ""
    ).strip()

    customer = request.form.get(
        "customer", ""
    ).strip()

    contact = request.form.get(
        "contact", ""
    ).strip()

    pickup = request.form.get(
        "pickup", ""
    ).strip()

    delivery_location = request.form.get(
        "delivery_location", ""
    ).strip()

    package = request.form.get(
        "package", ""
    ).strip()

    vehicle = request.form.get(
        "vehicle", ""
    ).strip()

    driver = request.form.get(
        "driver", ""
    ).strip()

    fields = [
        delivery_id,
        customer,
        contact,
        pickup,
        delivery_location,
        package,
        vehicle,
        driver
    ]

    if not all(fields):
        return redirect(
            url_for(
                "dashboard",
                error="All fields are required."
            )
        )

    for d in deliveries:

        if d["id"].lower() == delivery_id.lower():
            return redirect(
                url_for(
                    "dashboard",
                    error="Delivery ID already exists."
                )
            )

    selected_vehicle = None

    for v in vehicles:

        if v["id"] == vehicle:
            selected_vehicle = v
            break

    if selected_vehicle is None:
        return redirect(
            url_for(
                "dashboard",
                error="Invalid vehicle selected."
            )
        )

    for d in deliveries:

        if (
            d["vehicle"] == vehicle
            and d["status"] in ["Assigned", "In Transit"]
        ):
            return redirect(
                url_for(
                    "dashboard",
                    error="This vehicle is already assigned."
                )
            )

    deliveries.append(
        {
            "id": delivery_id,
            "customer": customer,
            "contact": contact,
            "pickup": pickup,
            "delivery_location": delivery_location,
            "package": package,
            "vehicle": vehicle,
            "driver": driver,
            "status": "Pending"
        }
    )

    return redirect(
        url_for(
            "dashboard",
            success="Delivery added successfully."
        )
    )


@app.route("/update_status/<delivery_id>", methods=["POST"])
def update_status(delivery_id):

    new_status = request.form.get("status", "")

    valid_statuses = [
        "Pending",
        "Assigned",
        "In Transit",
        "Delivered",
        "Cancelled"
    ]

    if new_status not in valid_statuses:
        return redirect(
            url_for(
                "dashboard",
                error="Invalid status."
            )
        )

    for d in deliveries:

        if d["id"] == delivery_id:

            if new_status in ["Assigned", "In Transit"]:

                for other in deliveries:

                    if (
                        other["id"] != delivery_id
                        and other["vehicle"] == d["vehicle"]
                        and other["status"] in [
                            "Assigned",
                            "In Transit"
                        ]
                    ):
                        return redirect(
                            url_for(
                                "dashboard",
                                error="Vehicle is already assigned to another delivery."
                            )
                        )

            d["status"] = new_status

            return redirect(
                url_for(
                    "dashboard",
                    success="Delivery status updated."
                )
            )

    return redirect(
        url_for(
            "dashboard",
            error="Delivery not found."
        )
    )


if __name__ == "__main__":
    app.run(debug=True)

