
"use strict";

const FIREBASE_URL = "https*******************atabase.app";

const CONTROL_URL = FIREBASE_URL + "/control.json";
const HANDS_BASE = "https:*************************75469240/";

const CONFIG = {
  confirmFrames: 3,
  handLossGraceMs: 200,
  watchdogMs: 500,
  heartbeatMs: 200,
  sendTickMs: 40,
  minSendIntervalMs: 50,
  requestTimeoutMs: 2500,
  steerDeadAngle: 4,
  steerMaxAngle: 38,
  steerSmoothing: 0.35,
  steerQuantum: 0.02,
  minHandSeparation: 0.12,
  fingerOpenRatio: 1.45
};

const FINGERS = [[8, 5], [12, 9], [16, 13], [20, 17]];

const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const commandBox = document.getElementById("command");
const hintBox = document.getElementById("hint");
const connectionBox = document.getElementById("connection");
const steerDot = document.getElementById("steerDot");
const steerValue = document.getElementById("steerValue");
const startButton = document.getElementById("start");
const stopButton = document.getElementById("stop");
const leftPoint = document.getElementById("leftPoint");
const rightPoint = document.getElementById("rightPoint");

let hands = null;
let stream = null;
let running = false;
let starting = false;
let processing = false;
let session = 0;
let cameraError = "";

const output = { key: "NONE", steering: 0, space: false };

let smoothSteering = 0;
let smoothLeft = null;
let smoothRight = null;

let pendingGesture = "NONE";
let pendingCount = 0;
let committedGesture = "NONE";

let lastResultAt = 0;
let handsLostSince = 0;

let firebaseState = "idle";
let lastSentSig = "";
let lastAttemptAt = 0;
let inFlight = false;
let activeController = null;
let sendSeq = 0;
let urgentFlag = false;

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);

  canvas.width = Math.round(rect.width * dpr);
  canvas.height = Math.round(rect.height * dpr);

  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

window.addEventListener("resize", resizeCanvas);
resizeCanvas();

function setStatus(text, type = "") {
  connectionBox.textContent = text;
  connectionBox.className = "connection " + type;
}

function refreshStatus() {
  if (firebaseState === "error") {
    setStatus("FIREBASE ERROR", "error");
  } else if (cameraError) {
    setStatus(cameraError, "error");
  } else if (starting) {
    setStatus("STARTING CAMERA");
  } else if (running) {
    setStatus("SYSTEM ONLINE", "online");
  } else {
    setStatus("CAMERA OFF");
  }
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function isNeutral() {
  return output.key === "NONE" && output.steering === 0 && !output.space;
}

function updateSteeringUI(value) {
  const percent = Math.round(value * 100);
  steerDot.style.left = (50 - value * 46) + "%";
  steerValue.textContent =
    (percent > 0 ? "LEFT " : percent < 0 ? "RIGHT " : "") +
    Math.abs(percent) + "%";
}

function setOutput(key, steering, space) {
  const quantized =
    Math.round(steering / CONFIG.steerQuantum) * CONFIG.steerQuantum;

  output.key = key;
  output.steering = Number(quantized.toFixed(3)) + 0;
  output.space = space;
  updateSteeringUI(output.steering);
}

function releaseOutput() {
  setOutput("NONE", 0, false);
  smoothSteering = 0;
  pendingGesture = "NONE";
  pendingCount = 0;
  committedGesture = "NONE";
  urgentFlag = true;
}

function buildPacket() {
  return {
    key: output.key,
    steering: output.steering,
    space: output.space,
    timestamp: Date.now()
  };
}

function signature() {
  return output.key + "|" + output.steering + "|" + output.space;
}

async function sendPacket(urgent) {
  if (inFlight) {
    if (!urgent) return;
    if (activeController) activeController.abort();
  }

  const controller = new AbortController();
  const timer = setTimeout(
    () => controller.abort(),
    CONFIG.requestTimeoutMs
  );
  const seq = ++sendSeq;
  const packet = buildPacket();
  const sig = signature();

  activeController = controller;
  inFlight = true;
  lastAttemptAt = Date.now();

  try {
    const response = await fetch(CONTROL_URL, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(packet),
      cache: "no-store",
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error("Firebase HTTP " + response.status);
    }

    if (seq === sendSeq) {
      lastSentSig = sig;
      firebaseState = "ok";
    }
  } catch (error) {
    if (seq === sendSeq) {
      firebaseState = "error";
      console.error("Firebase:", error);
    }
  } finally {
    clearTimeout(timer);
    if (seq === sendSeq) {
      inFlight = false;
      activeController = null;
    }
  }

  refreshStatus();
}

function tick() {
  const now = Date.now();

  if (running && !isNeutral() && now - lastResultAt > CONFIG.watchdogMs) {
    releaseOutput();
    commandBox.textContent = "WAIT";
    hintBox.textContent = "Tracking lost • Controls released";
  }

  if (urgentFlag) {
    urgentFlag = false;
    sendPacket(true);
    return;
  }

  const since = now - lastAttemptAt;
  const changed = signature() !== lastSentSig;
  const minGap =
    firebaseState === "error" ? 500 : CONFIG.minSendIntervalMs;
  const heartbeatDue = running && since >= CONFIG.heartbeatMs;

  if ((changed && since >= minGap) || heartbeatDue) {
    sendPacket(false);
  }
}

setInterval(tick, CONFIG.sendTickMs);

function mapLandmark(point) {
  const cw = canvas.clientWidth;
  const ch = canvas.clientHeight;
  const vw = video.videoWidth || 1280;
  const vh = video.videoHeight || 720;
  const scale = Math.max(cw / vw, ch / vh);
  const dw = vw * scale;
  const dh = vh * scale;

  return {
    x: (cw - dw) / 2 + (1 - point.x) * dw,
    y: (ch - dh) / 2 + point.y * dh
  };
}

function pixelDistance(a, b, vw, vh) {
  return Math.hypot((a.x - b.x) * vw, (a.y - b.y) * vh);
}

function countOpenFingers(hand, vw, vh) {
  const wrist = hand[0];
  let open = 0;

  for (const [tip, mcp] of FINGERS) {
    const base = Math.max(pixelDistance(hand[mcp], wrist, vw, vh), 1e-6);
    const reach = pixelDistance(hand[tip], wrist, vw, vh);

    if (reach / base > CONFIG.fingerOpenRatio) open++;
  }

  return open;
}

function getGesture(hand, vw, vh) {
  const open = countOpenFingers(hand, vw, vh);

  if (open === 0) return "FIST";
  if (open === 4) return "OPEN";
  return "OTHER";
}

function smoothPoint(oldPoint, nextPoint) {
  if (!oldPoint) return { ...nextPoint };

  return {
    x: oldPoint.x + (nextPoint.x - oldPoint.x) * 0.35,
    y: oldPoint.y + (nextPoint.y - oldPoint.y) * 0.35
  };
}

function drawHands(leftScreen, rightScreen) {
  ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);

  smoothLeft = smoothPoint(smoothLeft, leftScreen);
  smoothRight = smoothPoint(smoothRight, rightScreen);

  leftPoint.hidden = false;
  rightPoint.hidden = false;

  leftPoint.style.left = smoothLeft.x + "px";
  leftPoint.style.top = smoothLeft.y + "px";
  rightPoint.style.left = smoothRight.x + "px";
  rightPoint.style.top = smoothRight.y + "px";

  const gradient = ctx.createLinearGradient(
    smoothLeft.x, smoothLeft.y,
    smoothRight.x, smoothRight.y
  );

  gradient.addColorStop(0, "#00e5ff");
  gradient.addColorStop(.5, "#ffffff");
  gradient.addColorStop(1, "#a855f7");

  ctx.beginPath();
  ctx.moveTo(smoothLeft.x, smoothLeft.y);
  ctx.quadraticCurveTo(
    (smoothLeft.x + smoothRight.x) / 2,
    (smoothLeft.y + smoothRight.y) / 2 - 12,
    smoothRight.x,
    smoothRight.y
  );

  ctx.lineWidth = 4;
  ctx.strokeStyle = gradient;
  ctx.shadowBlur = 16;
  ctx.shadowColor = "#00e5ff";
  ctx.stroke();
  ctx.shadowBlur = 0;
}

function hideHandMarkers() {
  leftPoint.hidden = true;
  rightPoint.hidden = true;
  smoothLeft = null;
  smoothRight = null;
  ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);
}

function handleHandsLost(now) {
  hideHandMarkers();

  commandBox.textContent = "WAIT";
  hintBox.textContent = "Show both hands to control the car";

  if (!handsLostSince) handsLostSince = now;

  if (now - handsLostSince >= CONFIG.handLossGraceMs && !isNeutral()) {
    releaseOutput();
  }
}

function computeSteering(leftHand, rightHand, vw, vh) {
  const dxNorm = Math.abs(leftHand[9].x - rightHand[9].x);

  if (dxNorm < CONFIG.minHandSeparation) return 0;

  const dx = dxNorm * vw;
  const dy = (leftHand[9].y - rightHand[9].y) * vh;
  const angle = Math.atan2(dy, dx) * 180 / Math.PI;
  const magnitude = Math.abs(angle);

  if (magnitude <= CONFIG.steerDeadAngle) return 0;

  const span = CONFIG.steerMaxAngle - CONFIG.steerDeadAngle;

  return Math.sign(angle) *
    Math.min(1, (magnitude - CONFIG.steerDeadAngle) / span);
}

function onResults(results) {
  if (!running) return;

  const now = Date.now();
  lastResultAt = now;

  const detected = results.multiHandLandmarks || [];

  if (detected.length < 2) {
    handleHandsLost(now);
    return;
  }

  handsLostSince = 0;

  const vw = video.videoWidth || 1280;
  const vh = video.videoHeight || 720;

  const entries = detected
    .slice(0, 2)
    .map(hand => ({ hand, point: mapLandmark(hand[9]) }))
    .sort((a, b) => a.point.x - b.point.x);

  const leftHand = entries[0].hand;
  const rightHand = entries[1].hand;

  drawHands(entries[0].point, entries[1].point);

  const leftGesture = getGesture(leftHand, vw, vh);
  const rightGesture = getGesture(rightHand, vw, vh);

  const target = computeSteering(leftHand, rightHand, vw, vh);
  const alpha = target === 0 ? 0.5 : CONFIG.steerSmoothing;

  smoothSteering += (target - smoothSteering) * alpha;

  if (Math.abs(smoothSteering) < 0.03) smoothSteering = 0;

  let candidate = "NONE";

  if (leftGesture === "FIST" && rightGesture === "FIST") {
    candidate = "UP";
  } else if (leftGesture === "OPEN" && rightGesture === "OPEN") {
    candidate = "DOWN";
  } else if (
    (leftGesture === "FIST" && rightGesture === "OPEN") ||
    (leftGesture === "OPEN" && rightGesture === "FIST")
  ) {
    candidate = "SPACE";
  }

  if (candidate === pendingGesture) {
    pendingCount++;
  } else {
    pendingGesture = candidate;
    pendingCount = 1;
  }

  if (pendingCount >= CONFIG.confirmFrames) {
    committedGesture = pendingGesture;
  }

  let key = "NONE";
  let space = false;
  let label = "READY";
  let hint = "Tilt your hands to steer";

  if (committedGesture === "UP") {
    key = "UP";
    label = "ACCELERATE";
    hint = "Both fists • Keep steering by tilting";
  } else if (committedGesture === "DOWN") {
    key = "DOWN";
    label = "BRAKE";
    hint = "Both hands open • Keep steering by tilting";
  } else if (committedGesture === "SPACE") {
    space = true;
    label = "SPACE";
    hint = "Mixed hands • Special action";
  } else if (smoothSteering > 0.12) {
    label = "← LEFT";
    hint = "Tilt detected • Smooth steering";
  } else if (smoothSteering < -0.12) {
    label = "RIGHT →";
    hint = "Tilt detected • Smooth steering";
  }

  commandBox.textContent = label;
  hintBox.textContent = hint;

  setOutput(key, smoothSteering, space);
}

function startFrameLoop(mySession) {
  const useCallback = "requestVideoFrameCallback" in HTMLVideoElement.prototype;

  const schedule = () => {
    if (useCallback) {
      video.requestVideoFrameCallback(step);
    } else {
      requestAnimationFrame(step);
    }
  };

  const step = async () => {
    if (!running || mySession !== session) return;

    if (!processing && hands && video.readyState >= 2) {
      processing = true;

      try {
        await hands.send({ image: video });
      } catch (error) {
        if (running && mySession === session) console.error(error);
      } finally {
        processing = false;
      }
    }

    if (!running || mySession !== session) return;
    schedule();
  };

  schedule();
}

function releaseMedia(localStream, localHands) {
  if (localStream) {
    localStream.getTracks().forEach(track => track.stop());
  }

  if (localHands) {
    try { localHands.close(); } catch (_) {}
  }
}

async function startCamera() {
  if (running || starting) return;

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    cameraError = "HTTPS REQUIRED";
    hintBox.textContent =
      "Open this page over HTTPS or localhost to use the camera";
    refreshStatus();
    return;
  }

  starting = true;
  cameraError = "";
  const mySession = ++session;
  let localStream = null;
  let localHands = null;
  refreshStatus();

  try {
    localStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: "user",
        width: { ideal: 1280 },
        height: { ideal: 720 },
        frameRate: { ideal: 30, max: 30 }
      },
      audio: false
    });

    if (mySession !== session) {
      releaseMedia(localStream, null);
      return;
    }

    video.srcObject = localStream;
    await video.play();

    localHands = new Hands({
      locateFile: file => HANDS_BASE + file
    });

    localHands.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.65,
      minTrackingConfidence: 0.6
    });

    localHands.onResults(onResults);
    await localHands.initialize();

    if (mySession !== session) {
      releaseMedia(localStream, localHands);
      return;
    }

    stream = localStream;
    hands = localHands;
    running = true;
    lastResultAt = Date.now();
    handsLostSince = 0;

    startButton.textContent = "✓ CAMERA RUNNING";
    commandBox.textContent = "READY";
    hintBox.textContent = "Show both hands";

    startFrameLoop(mySession);
  } catch (error) {
    console.error(error);
    releaseMedia(localStream, localHands);
    stream = null;
    hands = null;
    running = false;
    video.srcObject = null;
    cameraError = "CAMERA ERROR";
    hintBox.textContent = "Allow camera permission and reload the page";
  } finally {
    starting = false;
    refreshStatus();
  }
}

async function stopCamera() {
  session++;
  running = false;

  releaseOutput();
  urgentFlag = false;
  updateSteeringUI(0);

  commandBox.textContent = "STOPPED";
  hintBox.textContent = "Controls released";

  const oldStream = stream;
  const oldHands = hands;
  stream = null;
  hands = null;

  releaseMedia(oldStream, oldHands);
  video.srcObject = null;

  hideHandMarkers();
  startButton.textContent = "▶ START CAMERA";
  cameraError = "";
  refreshStatus();

  await sendPacket(true);
}

startButton.addEventListener("click", startCamera);
stopButton.addEventListener("click", stopCamera);

document.addEventListener("visibilitychange", () => {
  if (document.hidden && !isNeutral()) releaseOutput();
});

window.addEventListener("pagehide", () => {
  running = false;
  session++;

  try {
    fetch(CONTROL_URL, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        key: "NONE",
        steering: 0,
        space: false,
        timestamp: Date.now()
      }),
      keepalive: true
    });
  } catch (_) {}

  releaseMedia(stream, hands);
});

releaseOutput();
refreshStatus();