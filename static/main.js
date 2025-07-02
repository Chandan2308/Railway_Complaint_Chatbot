document.getElementById("chatForm").addEventListener("submit", function(event) {
    event.preventDefault();  // Prevent form from reloading the page

    let inputField = document.getElementById("userInput");
    let chatBox = document.getElementById("chatBox");
    let userText = inputField.value.trim();

    if (userText === "") return;  // Ignore empty input

    // Add user message to chat
    chatBox.innerHTML += `<p><strong>You:</strong> ${userText}</p>`;    
    inputField.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    // Send data to Flask using Fetch API
    fetch("/process_complaint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ complaint: userText }),
    })
    .then(response => response.json())
    .then(data => {
        // Add bot response to chat
        chatBox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
        chatBox.scrollTop = chatBox.scrollHeight;

        // Show toast notification only if category exists
        if (data.category) {
            showToast(data.category);
        }

        saveComplaint(userText, data.category);

    })
    .catch(error => console.error("Error:", error));
});

// Function to show toast notification
function showToast(message) {
    let toast = document.getElementById("toastMessage");
    toast.innerText = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}

// Function to save complaints in localStorage
function saveComplaint(complaint, category) {
    let complaints = JSON.parse(localStorage.getItem("complaints")) || [];
    complaints.push({ complaint, category });
    localStorage.setItem("complaints", JSON.stringify(complaints));
}

// Load complaints in the View Complaints page
function loadComplaints() {
    let complaintsBox = document.getElementById("complaintsBox");
    let complaints = JSON.parse(localStorage.getItem("complaints")) || [];

    if (complaints.length === 0) {
        complaintsBox.innerHTML = "<p>No complaints yet.</p>";
    } else {
        complaintsBox.innerHTML = "";
        complaints.forEach((comp, index) => {
            complaintsBox.innerHTML += `<p><strong>${index + 1}. ${comp.complaint}</strong> - ${comp.category}</p>`;
        });
    }
}