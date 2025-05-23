console.log("Admin send email script loaded");

document.addEventListener("DOMContentLoaded", function () {
    // Handle click on "Send Email" button
    document.querySelectorAll(".send-email-btn").forEach(button => {
        button.addEventListener("click", function () {
            const id = this.dataset.id;
            const form = document.getElementById("form-" + id);
            form.style.display = "block"; // Show the form
        });
    });

    // Handle click on "Cancel" button
    document.querySelectorAll(".email-cancel-btn").forEach(cancelBtn => {
        cancelBtn.addEventListener("click", function (e) {
            e.preventDefault();  // Prevent the default form submit behavior
            const form = this.closest(".email-form-container");
            form.style.display = "none"; // Hide the form
        });
    });

    // Handle click on "Send" button
    document.querySelectorAll(".email-send-btn").forEach(sendBtn => {
        sendBtn.addEventListener("click", function (e) {
            e.preventDefault(); // Prevent form submission or page refresh

            const id = this.dataset.id;
            const form = document.getElementById("form-" + id);
            const emailInput = form.querySelector(".email-input");

            const email = emailInput.value;

            if (!email) {
                alert("Please enter an email address.");
                return;
            }

            // Get additional campaign data
            const campaignRow = this.closest('tr');
            const name = campaignRow.querySelector('td:nth-child(1)').innerText;
            const startedAt = campaignRow.querySelector('td:nth-child(3)').innerText;
            const createdAt = campaignRow.querySelector('td:nth-child(6)').innerText;
            const updatedAt = campaignRow.querySelector('td:nth-child(7)').innerText;

            // Send the email along with campaign data via an API request
            fetch("/campaign/email", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken"),
                },
                body: JSON.stringify({
                    email: email,
                    campaign_name: name,
                    started_at: startedAt,
                    created_at: createdAt,
                    updated_at: updatedAt
                })
            })
            .then(res => res.json())
            .then(data => {
                alert(data.message || "Email sent successfully!");
                form.style.display = "none"; // Optionally hide the form again
            })
            .catch(err => {
                console.error(err);
                alert("Something went wrong.");
            });
        });
    });
});

// Helper function to get the CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
