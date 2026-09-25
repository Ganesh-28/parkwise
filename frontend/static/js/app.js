const entryForm = document.getElementById("entryForm");

if (entryForm) {
    entryForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const vehicleNumber =
            document.getElementById("vehicleNumber").value;

        const vehicleType =
            document.getElementById("vehicleType").value;

        const message =
            document.getElementById("entryMessage");

        const ticketResult =
            document.getElementById("ticketResult");

        message.className = "message";
        message.textContent = "";

        ticketResult.classList.add("hidden");

        try {
            const response = await fetch("/api/entry/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    vehicle_number: vehicleNumber,
                    vehicle_type: vehicleType
                })
            });

            const data = await response.json();

            if (!data.success) {
                message.className = "message error";
                message.textContent = data.message;
                return;
            }

            document.getElementById("resultTicket").textContent =
                data.ticket_number;

            document.getElementById("resultVehicle").textContent =
                data.vehicle_number;

            document.getElementById("resultType").textContent =
                data.vehicle_type;

            document.getElementById("resultSlot").textContent =
                data.slot;

            ticketResult.classList.remove("hidden");

            entryForm.reset();

        } catch (error) {
            console.error("Entry request failed:", error);

            message.className = "message error";
            message.textContent =
                "Unable to connect to the server.";
        }
    });
}


const exitForm = document.getElementById("exitForm");

if (exitForm) {

    const params =
        new URLSearchParams(window.location.search);

    const ticketFromDashboard =
        params.get("ticket");

    if (ticketFromDashboard) {
        const ticketInput =
            document.getElementById("ticketNumber");

        if (ticketInput) {
            ticketInput.value = ticketFromDashboard;
        }
    }

    exitForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const ticketNumber =
            document.getElementById("ticketNumber").value;

        const paymentMethod =
            document.getElementById("paymentMethod").value;

        const message =
            document.getElementById("exitMessage");

        const paymentResult =
            document.getElementById("paymentResult");

        message.className = "message";
        message.textContent = "";

        paymentResult.classList.add("hidden");

        try {
            const response = await fetch("/api/exit/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    ticket_number: ticketNumber,
                    payment_method: paymentMethod
                })
            });

            const data = await response.json();

            if (!data.success) {
                message.className = "message error";
                message.textContent = data.message;
                return;
            }

            document.getElementById("exitTicket").textContent =
                data.ticket_number;

            document.getElementById("exitVehicle").textContent =
                data.vehicle_number;

            document.getElementById("exitType").textContent =
                data.vehicle_type;

            document.getElementById("exitSlot").textContent =
                data.slot;

            document.getElementById("exitStay").textContent =
                data.stay_minutes + " minutes";

            document.getElementById("exitPayment").textContent =
                data.payment_method;

            document.getElementById("exitAmount").textContent =
                "₹" + data.amount;

            paymentResult.classList.remove("hidden");

            exitForm.reset();

            window.history.replaceState(
                {},
                document.title,
                "/exit/"
            );

        } catch (error) {
            console.error("Exit request failed:", error);

            message.className = "message error";
            message.textContent =
                "Unable to connect to the server.";
        }
    });
}


const dashboardPage =
    document.getElementById("slotGrid");


async function loadDashboard() {

    console.log("Loading dashboard...");

    try {
        const response =
            await fetch("/api/dashboard/");

        if (!response.ok) {
            throw new Error(
                "Dashboard API returned HTTP " +
                response.status
            );
        }

        const data =
            await response.json();

        console.log("Dashboard data:", data);

        if (!data.success) {
            console.error(
                "Dashboard API error:",
                data
            );
            return;
        }

        const totalSlots =
            document.getElementById("totalSlots");

        const occupiedSlots =
            document.getElementById("occupiedSlots");

        const availableSlots =
            document.getElementById("availableSlots");

        const totalRevenue =
            document.getElementById("totalRevenue");

        if (totalSlots) {
            totalSlots.textContent =
                data.total_slots;
        }

        if (occupiedSlots) {
            occupiedSlots.textContent =
                data.occupied_slots;
        }

        if (availableSlots) {
            availableSlots.textContent =
                data.available_slots;
        }

        if (totalRevenue) {
            totalRevenue.textContent =
                "₹" + data.total_revenue;
        }


        const twoWheelerOccupied =
            document.getElementById(
                "twoWheelerOccupied"
            );

        const fourWheelerOccupied =
            document.getElementById(
                "fourWheelerOccupied"
            );

        const blockedSlots =
            document.getElementById(
                "blockedSlots"
            );

        if (twoWheelerOccupied) {
            twoWheelerOccupied.textContent =
                data.two_wheeler_occupied;
        }

        if (fourWheelerOccupied) {
            fourWheelerOccupied.textContent =
                data.four_wheeler_occupied;
        }

        if (blockedSlots) {
            blockedSlots.textContent =
                data.blocked_slots;
        }


        const pendingTickets =
            document.getElementById(
                "pendingTickets"
            );

        const pendingCount =
            document.getElementById(
                "pendingCount"
            );

        if (pendingCount) {
            pendingCount.textContent =
                data.pending_tickets
                    ? data.pending_tickets.length
                    : 0;
        }

        if (pendingTickets) {

            pendingTickets.innerHTML = "";

            if (
                !data.pending_tickets ||
                data.pending_tickets.length === 0
            ) {

                pendingTickets.innerHTML = `
                    <tr>
                        <td colspan="6" class="empty-table">
                            No pending tickets.
                        </td>
                    </tr>
                `;

            } else {

                data.pending_tickets.forEach(
                    function (ticket) {

                        const row =
                            document.createElement("tr");

                        const entryDate =
                            new Date(ticket.entry_time);

                        const formattedEntryTime =
                            entryDate.toLocaleString();

                        row.innerHTML = `
                            <td>
                                <strong>
                                    ${ticket.ticket_number}
                                </strong>
                            </td>

                            <td>
                                ${ticket.vehicle_number}
                            </td>

                            <td>
                                ${ticket.vehicle_type}
                            </td>

                            <td>
                                <span class="slot-tag">
                                    ${ticket.slot}
                                </span>
                            </td>

                            <td>
                                ${formattedEntryTime}
                            </td>

                            <td>
                                <a
                                    href="/exit/?ticket=${encodeURIComponent(ticket.ticket_number)}"
                                    class="process-exit-btn"
                                >
                                    Process Exit
                                </a>
                            </td>
                        `;

                        pendingTickets.appendChild(row);
                    }
                );
            }
        }


        const slotGrid =
            document.getElementById("slotGrid");

        if (slotGrid) {

            slotGrid.innerHTML = "";

            data.slots.forEach(
                function (slotData) {

                    const slot =
                        document.createElement("div");

                    slot.className = "slot";

                    if (
                        slotData.status ===
                        "BLOCKED"
                    ) {

                        slot.classList.add("blocked");

                        slot.innerHTML = `
                            <strong>${slotData.code}</strong>
                            <small>Blocked</small>
                        `;

                    } else if (
                        slotData.status ===
                        "OCCUPIED"
                    ) {

                        slot.classList.add("occupied");

                        slot.innerHTML = `
                            <strong>${slotData.code}</strong>
                            <small>Occupied</small>
                        `;

                    } else {

                        slot.classList.add("available");

                        slot.innerHTML = `
                            <strong>${slotData.code}</strong>
                            <small>Available</small>
                        `;
                    }

                    slotGrid.appendChild(slot);
                }
            );
        }


        const recentTickets =
            document.getElementById(
                "recentTickets"
            );

        if (recentTickets) {

            recentTickets.innerHTML = "";

            if (
                !data.recent_tickets ||
                data.recent_tickets.length === 0
            ) {

                recentTickets.innerHTML = `
                    <tr>
                        <td colspan="6" class="empty-table">
                            No parking activity yet.
                        </td>
                    </tr>
                `;

            } else {

                data.recent_tickets.forEach(
                    function (ticket) {

                        const row =
                            document.createElement("tr");

                        const statusClass =
                            ticket.status === "PARKED"
                                ? "status-parked"
                                : "status-paid";

                        row.innerHTML = `
                            <td>
                                ${ticket.ticket_number}
                            </td>

                            <td>
                                ${ticket.vehicle_number}
                            </td>

                            <td>
                                ${ticket.vehicle_type}
                            </td>

                            <td>
                                ${ticket.slot}
                            </td>

                            <td class="${statusClass}">
                                ${ticket.status}
                            </td>

                            <td>
                                ₹${ticket.amount}
                            </td>
                        `;

                        recentTickets.appendChild(row);
                    }
                );
            }
        }

    } catch (error) {

        console.error(
            "Dashboard loading failed:",
            error
        );
    }
}


if (dashboardPage) {

    loadDashboard();

    const refreshButton =
        document.getElementById(
            "refreshDashboard"
        );

    if (refreshButton) {

        refreshButton.addEventListener(
            "click",
            loadDashboard
        );
    }
}