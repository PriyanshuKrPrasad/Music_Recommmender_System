const chatForm = document.getElementById("chatForm");
const chatbox = document.getElementById("chatbox");
const songsList = document.getElementById("songsList");

let currentMood = null;
let selectedPlatform = null;

const moods = ["Happy", "Sad", "Romantic", "Energetic", "Chill", "Angry", "Focus", "Sleep", "Motivational"];
const platforms = ["YouTube", "Spotify", "JioSaavn"];

chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const userInput = document.getElementById("userInput");
  const userText = userInput.value.trim();
  if (!userText) return;

  appendChat(userText, "user");

  const mood = detectMood(userText);
  if (mood) {
    currentMood = mood;
    appendChat(`🎵 You're feeling ${mood}. Where would you like to listen?`, "bot");
    showPlatformOptions();
  } else {
    appendChat("❌ Sorry, I didn’t recognize that mood. Try: " + moods.join(", "), "bot");
  }

  userInput.value = "";
});

function appendChat(message, sender) {
  const msg = document.createElement("div");
  msg.className = `chat-message ${sender}`;
  msg.textContent = message;
  chatbox.appendChild(msg);
  chatbox.scrollTop = chatbox.scrollHeight;
}

function detectMood(text) {
  text = text.toLowerCase();
  return moods.find(mood => text.includes(mood.toLowerCase())) || null;
}

function showPlatformOptions() {
  const btnContainer = document.createElement("div");
  btnContainer.className = "button-container";

  platforms.forEach(platform => {
    const btn = document.createElement("button");
    btn.textContent = platform;
    btn.onclick = () => {
      selectedPlatform = platform;
      handlePlatformChoice(platform);
      btnContainer.remove();
    };
    btnContainer.appendChild(btn);
  });

  chatbox.appendChild(btnContainer);
}

function handlePlatformChoice(platform) {
  appendChat(`🎧 Loading your ${currentMood} playlist from ${platform}...`, "bot");
  songsList.innerHTML = "";

  fetch("/get_songs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mood: currentMood, platform: platform })
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        appendChat(`⚠️ ${data.error}`, "bot");
        return;
      }

      displaySongs(data);
      showRefreshButton();
    })
    .catch(err => {
      console.error("Fetch error:", err);
      appendChat("❌ Failed to load playlist. Please try again.", "bot");
    });
}

function displaySongs(data) {
  songsList.innerHTML = "";

  if (data.platform === "YouTube") {
    data.songs.forEach(song => {
      const div = document.createElement("div");
      div.className = "song-card";
      div.innerHTML = `
        <p><strong>${song.name}</strong></p>
        <iframe width="100%" height="200" src="https://www.youtube.com/embed/${song.video_id}" frameborder="0" allowfullscreen></iframe>
      `;
      songsList.appendChild(div);
    });
  }

  else if (data.platform === "Spotify") {
    const iframe = document.createElement("iframe");
    iframe.style.borderRadius = "12px";
    iframe.src = data.playlist;
    iframe.width = "100%";
    iframe.height = "380";
    iframe.allow = "autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture";
    iframe.loading = "lazy";
    iframe.frameBorder = "0";
    songsList.appendChild(iframe);
  }

  else if (data.platform === "JioSaavn") {
    data.songs.forEach(song => {
      const div = document.createElement("div");
      div.className = "song-card";
      div.innerHTML = `
        <p><strong>${song.name}</strong></p>
        <a href="${song.link}" target="_blank">${song.link}</a>
      `;
      songsList.appendChild(div);
    });
  }
}

function showRefreshButton() {
  // Remove existing refresh buttons
  chatbox.querySelectorAll("button").forEach(btn => {
    if (btn.textContent.includes("Refresh")) btn.remove();
  });

  const refreshBtn = document.createElement("button");
  refreshBtn.textContent = "🔁 Refresh Recommendations";
  refreshBtn.onclick = () => {
    if (selectedPlatform) handlePlatformChoice(selectedPlatform);
  };
  chatbox.appendChild(refreshBtn);
}
