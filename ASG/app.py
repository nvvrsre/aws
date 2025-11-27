from flask import Flask, render_template_string
import socket
import urllib.request

app = Flask(__name__)

def get_az_region():
    md_url = "http://169.254.169.254"
    az = "Unknown"
    region = "Unknown"

    token = None
    # Try to get IMDSv2 token
    try:
        req = urllib.request.Request(
            f"{md_url}/latest/api/token",
            method="PUT",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
        )
        with urllib.request.urlopen(req, timeout=0.2) as resp:
            token = resp.read().decode()
    except Exception:
        # If token fails, we'll try without it (IMDSv1), or fall back to Unknown
        pass

    # Try to read AZ using token (if we have one)
    try:
        headers = {}
        if token:
            headers["X-aws-ec2-metadata-token"] = token

        req = urllib.request.Request(
            f"{md_url}/latest/meta-data/placement/availability-zone",
            headers=headers,
        )
        with urllib.request.urlopen(req, timeout=0.2) as resp:
            az = resp.read().decode().strip()
            if az and len(az) > 1:
                region = az[:-1]  # ap-south-1a -> ap-south-1
    except Exception:
        pass

    return az, region

PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Ushasree Technologies</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #020617;
      color: #e5e7eb;
      text-align: center;
      padding: 40px 16px;
    }
    .container {
      max-width: 1000px;
      margin: 0 auto;
    }
    .header-card {
      background: #0f172a;
      padding: 24px;
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.6);
      margin-bottom: 24px;
    }
    h1 {
      color: #38bdf8;
      margin-bottom: 0.4rem;
    }
    h2 {
      color: #a855f7;
      margin-bottom: 0.3rem;
    }
    .subtitle {
      color: #9ca3af;
      margin-bottom: 0.6rem;
    }
    .ip {
      margin: 0.15rem 0;
      font-size: 0.95rem;
      color: #9ca3af;
    }
    .games-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 20px;
    }
    .card {
      background: #020617;
      border-radius: 16px;
      padding: 20px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      border: 1px solid #1f2937;
    }
    .badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 9999px;
      background: rgba(56,189,248,0.1);
      color: #38bdf8;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      margin-bottom: 6px;
    }
    input[type=number] {
      padding: 8px;
      border-radius: 8px;
      border: none;
      width: 120px;
      margin-top: 6px;
      text-align: center;
    }
    select {
      padding: 6px 10px;
      border-radius: 9999px;
      border: none;
      background: #020617;
      color: #e5e7eb;
      margin-top: 6px;
    }
    button {
      padding: 8px 16px;
      border-radius: 9999px;
      border: none;
      background: #22c55e;
      color:#022c22;
      font-weight:600;
      cursor:pointer;
      margin: 6px 4px;
    }
    button.secondary {
      background: #38bdf8;
      color: #082f49;
    }
    button.danger {
      background: #ef4444;
      color: #fee2e2;
    }
    button:hover {
      filter: brightness(1.1);
    }
    #guess-message, #guess-tries, #guess-score,
    #rps-message, #rps-score, #cpu-status {
      margin-top: 0.4rem;
      font-size: 0.9rem;
    }
    #guess-message, #rps-message {
      font-weight: 500;
    }
    .small {
      font-size: 0.8rem;
      color: #9ca3af;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header-card">
      <div class="badge">Hello All</div>
      <h1>Welcome to Ushasree Technologies</h1>
      <p class="subtitle">Demo on AWS Auto Scaling with fun sample games 🎮</p>
      <p class="ip">Server hostname: <strong>{{ hostname }}</strong></p>
      <p class="ip">Server IP address: <strong>{{ ip_address }}</strong></p>
      <p class="ip">Availability Zone: <strong>{{ az }}</strong></p>
      <p class="ip">Region: <strong>{{ region }}</strong></p>
    </div>

    <div class="games-grid">
      <!-- Game 1: Guess the Number -->
      <div class="card">
        <div class="badge">Game 1</div>
        <h2>Guess the Number</h2>
        <p class="small">
          Choose difficulty, then guess the secret number.  
          Your score goes up when you guess correctly with fewer attempts.
        </p>

        <div style="margin-top: 10px;">
          <label for="difficulty" class="small">Difficulty:</label><br>
          <select id="difficulty" onchange="resetGuessGame(true)">
            <option value="10">Easy (1 - 10)</option>
            <option value="20" selected>Medium (1 - 20)</option>
            <option value="50">Hard (1 - 50)</option>
          </select>
        </div>

        <div style="margin-top: 10px;">
          <input id="guess-input" type="number" placeholder="Your guess" />
        </div>
        <div style="margin-top: 8px;">
          <button onclick="makeGuess()">Guess</button>
          <button class="secondary" onclick="resetGuessGame(false)">New Number</button>
          <button class="danger" onclick="resetGuessScore()">Reset Score</button>
        </div>

        <p id="guess-message"></p>
        <p id="guess-tries"></p>
        <p id="guess-score"></p>
      </div>

      <!-- Game 2: Rock-Paper-Scissors -->
      <div class="card">
        <div class="badge">Game 2</div>
        <h2>Rock – Paper – Scissors</h2>
        <p class="small">
          Play against the server. First to 5 points wins the round!
        </p>

        <div style="margin-top: 10px;">
          <button onclick="playRPS('rock')">🪨 Rock</button>
          <button class="secondary" onclick="playRPS('paper')">📄 Paper</button>
          <button class="danger" onclick="playRPS('scissors')">✂️ Scissors</button>
        </div>

        <p id="rps-message"></p>
        <p id="rps-score"></p>
        <p class="small" id="rps-round"></p>
        <button style="margin-top: 6px;" onclick="resetRPS()">Reset Match</button>
      </div>

      <!-- Card 3: CPU Load Test -->
      <div class="card">
        <div class="badge">Load Demo</div>
        <h2>CPU Load Test</h2>
        <p class="small">
          Press the button to send multiple requests to the <code>/cpu</code> endpoint.  
          This will push CPU usage up so you can demo AWS Auto Scaling.
        </p>

        <div style="margin-top: 10px;">
          <button onclick="runCpuTest()">Start CPU Load Test</button>
          <button class="secondary" onclick="clearCpuStatus()">Clear Status</button>
        </div>

        <p id="cpu-status"></p>
      </div>
    </div>

    <p class="small" style="margin-top: 24px;">
      Backend: Python Flask • Deployed on AWS EC2 (Ubuntu)
    </p>
  </div>

  <script>
    // --------- Game 1: Guess the Number ----------
    let guessSecret = null;
    let guessMax = 20;
    let guessAttempts = 0;
    let guessScore = 0;

    function initGuessGame() {
      const difficultySelect = document.getElementById('difficulty');
      guessMax = parseInt(difficultySelect.value, 10) || 20;
      guessSecret = Math.floor(Math.random() * guessMax) + 1;
      guessAttempts = 0;
      document.getElementById('guess-message').textContent = "";
      document.getElementById('guess-tries').textContent = "";
      document.getElementById('guess-input').value = "";
      updateGuessScore();
    }

    function updateGuessScore() {
      document.getElementById('guess-score').textContent =
        "Score: " + guessScore + " points";
    }

    function makeGuess() {
      const input = document.getElementById('guess-input');
      const msg = document.getElementById('guess-message');
      const tries = document.getElementById('guess-tries');

      const value = parseInt(input.value, 10);

      if (guessSecret === null) {
        initGuessGame();
      }

      if (isNaN(value)) {
        msg.textContent = "Please enter a number.";
        return;
      }
      if (value < 1 || value > guessMax) {
        msg.textContent = "Please enter a number between 1 and " + guessMax + ".";
        return;
      }

      guessAttempts++;

      if (value === guessSecret) {
        msg.textContent = "🎉 Correct! " + value + " is the number.";
        const base = 10;
        const bonus = Math.max(1, base - guessAttempts + 1);
        guessScore += bonus;
        updateGuessScore();
        tries.textContent = "You needed " + guessAttempts + " attempts. (+" + bonus + " points)";
        guessSecret = Math.floor(Math.random() * guessMax) + 1;
        guessAttempts = 0;
      } else if (value < guessSecret) {
        msg.textContent = "Too low! Try a higher number.";
        tries.textContent = "Attempts so far: " + guessAttempts;
      } else {
        msg.textContent = "Too high! Try a lower number.";
        tries.textContent = "Attempts so far: " + guessAttempts;
      }
    }

    function resetGuessGame(fromDifficultyChange) {
      guessSecret = null;
      guessAttempts = 0;
      initGuessGame();
      const msg = document.getElementById('guess-message');
      const tries = document.getElementById('guess-tries');
      msg.textContent = fromDifficultyChange
        ? "Difficulty changed. New secret number generated."
        : "New secret number generated. Start guessing!";
      tries.textContent = "";
    }

    function resetGuessScore() {
      guessScore = 0;
      updateGuessScore();
      document.getElementById('guess-message').textContent = "Score reset.";
      document.getElementById('guess-tries').textContent = "";
    }

    // --------- Game 2: Rock-Paper-Scissors ----------
    let rpsPlayer = 0;
    let rpsServer = 0;
    let rpsRound = 1;

    function playRPS(playerChoice) {
      const options = ["rock", "paper", "scissors"];
      const serverChoice = options[Math.floor(Math.random() * options.length)];

      const msg = document.getElementById('rps-message');
      const score = document.getElementById('rps-score');
      const roundEl = document.getElementById('rps-round');

      let result = "";

      if (playerChoice === serverChoice) {
        result = "It's a draw!";
      } else if (
        (playerChoice === "rock" && serverChoice === "scissors") ||
        (playerChoice === "paper" && serverChoice === "rock") ||
        (playerChoice === "scissors" && serverChoice === "paper")
      ) {
        result = "You win this turn! 🎉";
        rpsPlayer++;
      } else {
        result = "Server wins this turn!";
        rpsServer++;
      }

      msg.textContent = "You chose " + playerChoice +
                        ", server chose " + serverChoice + ". " + result;
      score.textContent = "Score – You: " + rpsPlayer + " | Server: " + rpsServer;
      roundEl.textContent = "Round: " + rpsRound;
      rpsRound++;

      if (rpsPlayer >= 5 || rpsServer >= 5) {
        if (rpsPlayer > rpsServer) {
          msg.textContent += " 🏆 You won the match!";
        } else if (rpsServer > rpsPlayer) {
          msg.textContent += " 💻 Server won the match.";
        } else {
          msg.textContent += " The match is a draw.";
        }
      }
    }

    function resetRPS() {
      rpsPlayer = 0;
      rpsServer = 0;
      rpsRound = 1;
      document.getElementById('rps-message').textContent = "New match started. First to 5 points!";
      document.getElementById('rps-score').textContent = "";
      document.getElementById('rps-round').textContent = "";
    }

    // --------- CPU Load Test ----------
    let cpuRequestsTotal = 0;
    let cpuRequestsDone = 0;

    function runCpuTest() {
      const statusEl = document.getElementById('cpu-status');
      const total = 40;
      cpuRequestsTotal = total;
      cpuRequestsDone = 0;

      statusEl.textContent = "Starting CPU load test with " + total + " requests to /cpu...";

      for (let i = 0; i < total; i++) {
        fetch('/cpu')
          .then(() => {
            cpuRequestsDone++;
            if (cpuRequestsDone < cpuRequestsTotal) {
              statusEl.textContent =
                "CPU load test running... " + cpuRequestsDone + "/" + cpuRequestsTotal + " completed.";
            } else {
              statusEl.textContent =
                "CPU load test completed (" + cpuRequestsTotal + " requests). Check CloudWatch/ASG!";
            }
          })
          .catch(() => {
            cpuRequestsDone++;
            statusEl.textContent =
              "Some requests failed. Completed " + cpuRequestsDone + "/" + cpuRequestsTotal + ".";
          });
      }
    }

    function clearCpuStatus() {
      document.getElementById('cpu-status').textContent = "";
    }

    window.onload = function() {
      initGuessGame();
      resetRPS();
    }
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except Exception:
        ip_address = "Unknown"

    az, region = get_az_region()
    return render_template_string(
        PAGE,
        hostname=hostname,
        ip_address=ip_address,
        az=az,
        region=region,
    )

@app.route("/cpu")
def cpu():
    x = 0
    for i in range(50_000_000):
        x += i
    return f"CPU burn done: {x}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
