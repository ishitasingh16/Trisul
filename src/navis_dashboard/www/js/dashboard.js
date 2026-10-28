const ros = new ROSLIB.Ros({
  url: `ws://${window.location.hostname || 'localhost'}:9090`
});

const statusDot = document.getElementById('statusDot');
const connectionText = document.getElementById('connectionText');
const metricState = document.getElementById('metricState');
const metricTime = document.getElementById('metricTime');
const metricDistance = document.getElementById('metricDistance');
const metricLatency = document.getElementById('metricLatency');
const metricCollisions = document.getElementById('metricCollisions');
const objectsTableBody = document.getElementById('objectsTableBody');
const mapCanvas = document.getElementById('mapCanvas');
const radarCanvas = document.getElementById('radarCanvas');
const clearGoalBtn = document.getElementById('clearGoalBtn');

const mapCtx = mapCanvas.getContext('2d');
const radarCtx = radarCanvas.getContext('2d');

let robotPose = { x: 0, y: 0, yaw: 0 };
let currentPath = [];
let scanPoints = [];

function resizeCanvases() {
  mapCanvas.width = mapCanvas.parentElement.clientWidth;
  mapCanvas.height = mapCanvas.parentElement.clientHeight;
  radarCanvas.width = radarCanvas.parentElement.clientWidth;
  radarCanvas.height = radarCanvas.parentElement.clientHeight;
}
window.addEventListener('resize', resizeCanvases);
resizeCanvases();

ros.on('connection', () => {
  statusDot.classList.add('connected');
  connectionText.textContent = 'Connected (ROSBridge)';
});

ros.on('error', () => {
  statusDot.classList.remove('connected');
  connectionText.textContent = 'Connection Error';
});

ros.on('close', () => {
  statusDot.classList.remove('connected');
  connectionText.textContent = 'Disconnected';
});

const statusListener = new ROSLIB.Topic({
  ros: ros,
  name: '/world_model/status',
  messageType: 'navis_msgs/MissionStatus'
});

statusListener.subscribe((msg) => {
  metricState.textContent = msg.state || 'ACTIVE';
  const sec = Math.floor(msg.elapsed_time || 0);
  const hrs = Math.floor(sec / 3600).toString().padStart(2, '0');
  const mins = Math.floor((sec % 3600) / 60).toString().padStart(2, '0');
  const secs = (sec % 60).toString().padStart(2, '0');
  metricTime.textContent = `${hrs}:${mins}:${secs}`;
  metricDistance.textContent = `${(msg.distance_traveled || 0).toFixed(2)} m`;
  metricCollisions.textContent = msg.collision_count || 0;
});

const diagListener = new ROSLIB.Topic({
  ros: ros,
  name: '/diagnostics',
  messageType: 'diagnostic_msgs/DiagnosticArray'
});

diagListener.subscribe((msg) => {
  if (msg.status && msg.status.length > 0) {
    for (const val of msg.status[0].values) {
      if (val.key === 'Inference Latency (ms)') {
        metricLatency.textContent = `${parseFloat(val.value).toFixed(1)} ms`;
      }
    }
  }
});

const objectsListener = new ROSLIB.Topic({
  ros: ros,
  name: '/world_model/objects',
  messageType: 'navis_msgs/WorldObjectArray'
});

objectsListener.subscribe((msg) => {
  if (!msg.objects || msg.objects.length === 0) {
    objectsTableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--navis-text-muted);">No objects tracked</td></tr>';
    return;
  }
  objectsTableBody.innerHTML = '';
  for (const obj of msg.objects) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>#${obj.id}</td>
      <td style="color: var(--navis-accent-secondary); font-weight: 600;">${obj.class_name}</td>
      <td>(${obj.position.x.toFixed(2)}, ${obj.position.y.toFixed(2)})</td>
      <td><span class="badge" style="background: ${obj.is_dynamic ? 'var(--navis-accent-warning)' : 'var(--navis-bg-tertiary)'}">${obj.is_dynamic ? 'Dynamic' : 'Static'}</span></td>
    `;
    objectsTableBody.appendChild(tr);
  }
});

const odomListener = new ROSLIB.Topic({
  ros: ros,
  name: '/amcl_pose',
  messageType: 'geometry_msgs/PoseWithCovarianceStamped'
});

odomListener.subscribe((msg) => {
  const p = msg.pose.pose.position;
  const q = msg.pose.pose.orientation;
  const siny_cosp = 2 * (q.w * q.z + q.x * q.y);
  const cosy_cosp = 1 - 2 * (q.y * q.y + q.z * q.z);
  const yaw = Math.atan2(siny_cosp, cosy_cosp);
  robotPose = { x: p.x, y: p.y, yaw: yaw };
  drawMap();
});

const planListener = new ROSLIB.Topic({
  ros: ros,
  name: '/plan',
  messageType: 'nav_msgs/Path'
});

planListener.subscribe((msg) => {
  if (msg.poses) {
    currentPath = msg.poses.map(ps => ({ x: ps.pose.position.x, y: ps.pose.position.y }));
    drawMap();
  }
});

const scanListener = new ROSLIB.Topic({
  ros: ros,
  name: '/scan',
  messageType: 'sensor_msgs/LaserScan'
});

scanListener.subscribe((msg) => {
  scanPoints = [];
  const ranges = msg.ranges;
  for (let i = 0; i < ranges.length; i++) {
    const r = ranges[i];
    if (r >= msg.range_min && r <= msg.range_max) {
      const angle = msg.angle_min + i * msg.angle_increment;
      scanPoints.push({ x: r * Math.cos(angle), y: r * Math.sin(angle) });
    }
  }
  drawRadar();
});

const goalPublisher = new ROSLIB.Topic({
  ros: ros,
  name: '/goal_pose',
  messageType: 'geometry_msgs/PoseStamped'
});

mapCanvas.addEventListener('click', (e) => {
  const rect = mapCanvas.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const clickY = e.clientY - rect.top;

  const scale = 30;
  const originX = mapCanvas.width / 2;
  const originY = mapCanvas.height / 2;

  const targetX = (clickX - originX) / scale;
  const targetY = -(clickY - originY) / scale;

  const goalMsg = new ROSLIB.Message({
    header: { frame_id: 'map', stamp: { sec: 0, nanosec: 0 } },
    pose: {
      position: { x: targetX, y: targetY, z: 0.0 },
      orientation: { x: 0.0, y: 0.0, z: 0.0, w: 1.0 }
    }
  });

  goalPublisher.publish(goalMsg);
  drawMap();
});

clearGoalBtn.addEventListener('click', () => {
  currentPath = [];
  drawMap();
});

function drawMap() {
  mapCtx.fillStyle = '#1e293b';
  mapCtx.fillRect(0, 0, mapCanvas.width, mapCanvas.height);

  const scale = 30;
  const ox = mapCanvas.width / 2;
  const oy = mapCanvas.height / 2;

  mapCtx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
  mapCtx.lineWidth = 1;
  for (let x = 0; x < mapCanvas.width; x += scale) {
    mapCtx.beginPath();
    mapCtx.moveTo(x, 0);
    mapCtx.lineTo(x, mapCanvas.height);
    mapCtx.stroke();
  }
  for (let y = 0; y < mapCanvas.height; y += scale) {
    mapCtx.beginPath();
    mapCtx.moveTo(0, y);
    mapCtx.lineTo(mapCanvas.width, y);
    mapCtx.stroke();
  }

  if (currentPath.length > 1) {
    mapCtx.strokeStyle = '#22c55e';
    mapCtx.lineWidth = 3;
    mapCtx.beginPath();
    for (let i = 0; i < currentPath.length; i++) {
      const px = ox + currentPath[i].x * scale;
      const py = oy - currentPath[i].y * scale;
      if (i === 0) mapCtx.moveTo(px, py);
      else mapCtx.lineTo(px, py);
    }
    mapCtx.stroke();
  }

  const rx = ox + robotPose.x * scale;
  const ry = oy - robotPose.y * scale;

  mapCtx.fillStyle = '#3b82f6';
  mapCtx.beginPath();
  mapCtx.arc(rx, ry, 8, 0, Math.PI * 2);
  mapCtx.fill();

  mapCtx.strokeStyle = '#f1f5f9';
  mapCtx.lineWidth = 2;
  mapCtx.beginPath();
  mapCtx.moveTo(rx, ry);
  mapCtx.lineTo(rx + Math.cos(-robotPose.yaw) * 16, ry + Math.sin(-robotPose.yaw) * 16);
  mapCtx.stroke();
}

function drawRadar() {
  radarCtx.fillStyle = '#111827';
  radarCtx.fillRect(0, 0, radarCanvas.width, radarCanvas.height);

  const cx = radarCanvas.width / 2;
  const cy = radarCanvas.height / 2;
  const maxRange = 5.6;
  const scale = (Math.min(cx, cy) - 10) / maxRange;

  radarCtx.strokeStyle = 'rgba(6, 182, 212, 0.15)';
  radarCtx.lineWidth = 1;
  for (let r = 1.0; r <= maxRange; r += 1.5) {
    radarCtx.beginPath();
    radarCtx.arc(cx, cy, r * scale, 0, Math.PI * 2);
    radarCtx.stroke();
  }

  radarCtx.fillStyle = '#06b6d4';
  for (const pt of scanPoints) {
    const px = cx + pt.x * scale;
    const py = cy - pt.y * scale;
    radarCtx.fillRect(px - 1.5, py - 1.5, 3, 3);
  }

  radarCtx.fillStyle = '#3b82f6';
  radarCtx.beginPath();
  radarCtx.arc(cx, cy, 4, 0, Math.PI * 2);
  radarCtx.fill();
}
