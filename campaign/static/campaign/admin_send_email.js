console.log("Admin send email script loaded");

document.addEventListener("DOMContentLoaded", function () {
  // Handle click on "Send Email" button
  document.querySelectorAll(".send-email-btn").forEach((button) => {
    button.addEventListener("click", function () {
      const id = this.dataset.id;
      const form = document.getElementById("form-" + id);
      form.style.display = "block"; // Show the form
    });
  });

  // Handle click on "Cancel" button
  document.querySelectorAll(".email-cancel-btn").forEach((cancelBtn) => {
    cancelBtn.addEventListener("click", function (e) {
      e.preventDefault(); // Prevent the default form submit behavior
      const form = this.closest(".email-form-container");
      form.style.display = "none"; // Hide the form
    });
  });

  // Handle click on "Send" button
  document.querySelectorAll(".email-send-btn").forEach((sendBtn) => {
    sendBtn.addEventListener("click", function (e) {
      e.preventDefault(); // Prevent form submission or page refresh

      const campaignId = this.dataset.id;
      const form = document.getElementById("form-" + campaignId);
      const emailInput = form.querySelector(".email-input");
      const email = emailInput.value;

      if (!email) {
        alert("Please enter an email address.");
        return;
      }

      fetch("/campaign/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({
          email: email,
          campaign_id: campaignId,
        }),
      })
        .then((res) => {
          // Check if the response is ok first
          if (!res.ok) {
            // Log the response status and statusText for debugging
            console.error(`Error response: ${res.status} ${res.statusText}`);
            return res.text().then((text) => {
              // Try to parse as JSON, but fall back to text if it's not JSON
              try {
                return Promise.reject(JSON.parse(text));
              } catch (e) {
                return Promise.reject(text);
              }
            });
          }
          return res.json();
        })
        .then((data) => {
          console.log("Success response:", data);
          alert(data.message || "Email sent successfully!");
          form.style.display = "none"; // Hide the form after sending
        })
        .catch((err) => {
          // Improved error logging
          console.error("Error details:", err);

          // More informative error message
          if (typeof err === "object" && err.error) {
            alert(`Error: ${err.error}`);
          } else if (typeof err === "string") {
            alert(`Error: ${err}`);
          } else {
            alert("Something went wrong. Check console for details.");
          }
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
