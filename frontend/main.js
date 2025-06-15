document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById('uploadForm');
  const fileInput = document.getElementById('fileInput');
  const outputBox = document.getElementById('outputBox');
  const historyButton = document.getElementById('historyButton');
  const clearHistoryButton = document.getElementById('clearHistoryButton');
  const historyDiv = document.getElementById('history');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) return (outputBox.textContent = "Please select a file.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:5000/upload", {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      outputBox.textContent = res.ok ? data.output : `Error: ${data.error || "Unknown error"}`;
    } catch {
      outputBox.textContent = "Error connecting to backend.";
    }
  });

  historyButton.addEventListener('click', async () => {
    try {
      const res = await fetch("http://localhost:5000/history");
      const data = await res.json();

      historyDiv.innerHTML = "<h3>Upload History</h3>";
      data.forEach(entry => {
        const item = document.createElement('pre');
        item.textContent = `[${entry.timestamp}] ${entry.filename}\nOutput:\n${entry.output || "No output"}\n${entry.error ? 'Error:\n' + entry.error : ''}`;
        historyDiv.appendChild(item);
      });
    } catch {
      historyDiv.textContent = "Error loading history.";
    }
  });

  clearHistoryButton.addEventListener('click', async () => {
    if (!confirm("Are you sure you want to clear the history?")) return;

    try {
      const res = await fetch("http://localhost:5000/history/clear", { method: "POST" });
      if (res.ok) {
        historyDiv.innerHTML = "History cleared.";
      } else {
        historyDiv.innerHTML = "Failed to clear history.";
      }
    } catch {
      historyDiv.innerHTML = "Error contacting backend.";
    }
  });
});
