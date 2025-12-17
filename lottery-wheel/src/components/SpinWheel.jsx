import React, { useState, useRef } from "react";

const COLORS = ["#ff6b6b", "#4ecdc4", "#feca57", "#5f27cd"];

function normalizeAngle(angle) {
  return (angle % 360 + 360) % 360;
}

function assignColors(items, colorList) {
  const n = items.length;
  const result = [];
  for (let i = 0; i < n; i++) {
    let colorIndex = i % colorList.length;
    if (i > 0 && colorList[colorIndex] === result[i - 1]) {
      colorIndex = (colorIndex + 1) % colorList.length;
    }
    result.push(colorList[colorIndex]);
  }
  if (result[0] === result[n - 1]) {
    const alt = colorList.find(c => c !== result[0] && c !== result[n - 2]);
    result[n - 1] = alt || result[n - 1];
  }
  return result;
}

// API / local random
async function getRandomValue() {
  try {
    const res = await fetch("http://127.0.0.1:8000/api/random");
    if (!res.ok) throw new Error("API not available");
    const data = await res.json();
    return { value: data.rand, source: data.source || "unknown" };
  } catch (err) {
    console.error(err);
    return { value: Math.random(), source: "aip unused" };
  }
}

function calculateRotation(index, total) {
  const degreesPerOption = 360 / total;
  const singleRotation = 360 - index * degreesPerOption;
  return 360 * 5 + singleRotation;
}

function WheelSegment({ item, index, degreesPerOption, color }) {
  const startAngle = normalizeAngle(-degreesPerOption / 2);
  const endAngle = normalizeAngle(degreesPerOption / 2);
  return (
    <div
      style={{
        position: "absolute",
        width: "100%",
        height: "100%",
        borderRadius: "50%",
        transformOrigin: "center center",
        transform: `rotate(${index * degreesPerOption}deg)`,
        background: `conic-gradient(${color} 0deg, ${color} ${endAngle}deg, 
                     transparent ${endAngle}deg, transparent ${startAngle}deg, 
                     ${color} ${startAngle}deg)`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "white",
        fontSize: "30px"
      }}
    >
      <span
        style={{
          position: "absolute",
          top: "10%",
          left: "50%",
          transform: "translateX(-50%)",
          color: "white",
          fontSize: "30px",
          whiteSpace: "nowrap",
          pointerEvents: "none"
        }}
      >
        {item}
      </span>
    </div>
  );
}

export default function SpinWheel() {
  const [options, setOptions] = useState("");
  const [spinning, setSpinning] = useState(false);
  const [winner, setWinner] = useState(null);
  const [rngMode, setRngMode] = useState("aip unused");
  const wheelRef = useRef(null);

  const handleSpin = async () => {
    const list = options.split("\n").map(i => i.trim()).filter(Boolean);
    if (!list.length) return;

    setSpinning(true);
    setWinner(null);

    const { value: randomValue, source } = await getRandomValue();
    setRngMode(source);

    const winIndex = randomValue >= 1 ? list.length - 1 : Math.floor(randomValue * list.length);
    const totalRotation = calculateRotation(winIndex, list.length);

    if (wheelRef.current) {
      wheelRef.current.style.transition = "transform 3s ease-out";
      wheelRef.current.style.transform = `rotate(${totalRotation}deg)`;
    }

    setTimeout(() => {
      setSpinning(false);
      setWinner(list[winIndex]);
      if (wheelRef.current) {
        const degreesPerOption = 360 / list.length;
        const singleRotation = 360 - winIndex * degreesPerOption;
        wheelRef.current.style.transition = "none";
        wheelRef.current.style.transform = `rotate(${singleRotation}deg)`;
      }
    }, 3000);
  };

  const list = options.split("\n").map(i => i.trim()).filter(Boolean);
  const totalOptions = list.length;
  const degreesPerOption = 360 / Math.max(totalOptions, 1);
  const itemColors = assignColors(list, COLORS);
  const statusColor = rngMode === "microphone" ? "green" : rngMode === "fallback" ? "orange" : "gray";

  return (
    <div style={{ position: "relative", alignItems: "flex-start", padding: "0" }}>
      <h1>Lottery Wheel</h1>
      <div
        style={{
          position: "absolute",
          top: "10px",
          right: "10px",
          display: "flex",
          alignItems: "center",
          gap: "8px",
          padding: "6px 10px",
          background: "#fff",
          borderRadius: "8px",
          boxShadow: "0 2px 6px rgba(0,0,0,0.2)"
        }}
      >
        <span style={{ fontWeight: "bold" }}>RNG Mode: {rngMode}</span>
        <div
          style={{
            width: "12px",
            height: "12px",
            borderRadius: "50%",
            backgroundColor: statusColor
          }}
        />
      </div>

      <div style={{ justifyContent: "center", alignItems: "flex-start", display: "flex", gap: "2rem" }}>
        <div data-testid="wheel" style={{ width: "300px", height: "300px", position: "relative" }}>
          <div
            ref={wheelRef}
            style={{
              width: "100%",
              height: "100%",
              borderRadius: "50%",
              border: "5px solid #333",
              position: "relative",
              transform: "rotate(0deg)"
            }}
          >
            {list.map((item, index) => (
              <WheelSegment
                key={index}
                item={item}
                index={index}
                degreesPerOption={degreesPerOption}
                color={itemColors[index]}
              />
            ))}
          </div>

          {/* pointer */}
          <div
            style={{
              position: "absolute",
              top: "-10px",
              left: "50%",
              transform: "translateX(-25%)",
              width: "0",
              height: "0",
              borderLeft: "10px solid transparent",
              borderRight: "10px solid transparent",
              borderTop: "20px solid red",
              zIndex: 10
            }}
          />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <textarea
            value={options}
            onChange={e => setOptions(e.target.value)}
            rows={10}
            cols={20}
            placeholder="Enter options, one per line"
          />
          <button
            disabled={spinning}
            onClick={handleSpin}
            style={{
              padding: "0.5rem 1rem",
              fontSize: "1rem",
              backgroundColor: spinning ? "#999" : "#007bff",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: spinning ? "not-allowed" : "pointer"
            }}
          >
            {spinning ? "Spinning..." : "Start Lottery"}
          </button>
          {winner && <p style={{ fontWeight: "bold" }}>🎉 Winner: {winner}</p>}
        </div>
      </div>
    </div>
  );
}
