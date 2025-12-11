import { useState, useRef } from "react";

const colors = ["#ff6b6b", "#4ecdc4", "#feca57", "#5f27cd"];

function normalizeAngle(angle) {
    // check angle within 0 ~ 360
    return (angle % 360 + 360) % 360;
}

function assignColors(items, colorList) {
    const n = items.length;
    let result = [];

    for (let i = 0; i < n; i++) {
        // use color indexing for looping, but avoid repeating the previous one.
        let colorIndex = i % colorList.length;
        if (i > 0 && colorList[colorIndex] === result[i - 1]) {
            colorIndex = (colorIndex + 1) % colorList.length;
        }
        result.push(colorList[colorIndex]);
    }

    // if first and last are the same, change the last one
    if (result[0] === result[n - 1]) {
        const alt = colorList.find(
            c => c !== result[0] && c !== result[n - 2]
        );
        result[n - 1] = alt || result[n - 1];   // fallback to current if no alternative found (should not happen with 3+ colors, but just in case)
    }

    return result;
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

        let randomValue; // 0 ~ 1

        try {
            // try to call API on backend to get random number
            const res = await fetch("/api/random"); // not implemented yet
            if (res.ok) {
                const data = await res.json();
                randomValue = data.value; // API is expected to return { value: 0 ~ 1 }
                setRngMode(data.mode || "");  // API 需回傳 { value: 0~1, mode: "microphone" }
            } else {
                throw new Error("API is not available");
            }
        } catch (err) {
            // API failed or not available → fallback
            randomValue = Math.random();
        }

        // randomly select a index as the winner 
        let winIndex;
        // to avoid edge case where randomValue is exactly 1
        if (randomValue >= 1) {
            winIndex = list.length - 1;
        } else {
            winIndex = Math.floor(randomValue * list.length);
        }

        // transform 360 * n + targetAngle
        const totalOptions = list.length;
        const degreesPerOption = 360 / totalOptions;
        const singleRotation = 360 - winIndex * degreesPerOption;
        const totalRotation = 360 * 5 + singleRotation;   // turn 5 full rounds before stopping

        // start spinning
        if (wheelRef.current) {
            wheelRef.current.style.transition = "transform 3s ease-out";
            wheelRef.current.style.transform = `rotate(${totalRotation}deg)`;
        }

        setTimeout(() => {
            setSpinning(false);
            setWinner(list[winIndex]);
            // reset rotation to avoid large angle values
            if (wheelRef.current) {
                wheelRef.current.style.transition = "none";
                wheelRef.current.style.transform = `rotate(${singleRotation}deg)`;
            }
        }, 3000);
    };

    // generate wheel segments
    const list = options.split("\n").map(i => i.trim()).filter(Boolean);
    const totalOptions = list.length;
    const degreesPerOption = 360 / Math.max(totalOptions, 1);
    const itemColors = assignColors(list, colors);
    const statusColor = rngMode === "microphone" 
    ? "green" 
    : rngMode === "fallback" 
        ? "orange" 
        : "gray";

    return (
        <div style={{ position: "relative", alignItems: "flex-start", padding: "0" }}>
            <h1>Lottery Wheel</h1>
            <div style={{ 
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
            }}>
                <span style={{ fontWeight: "bold" }}>RNG Mode: {rngMode}</span>
                <div style={{
                    width: "12px",
                    height: "12px",
                    borderRadius: "50%",
                    backgroundColor: statusColor
                }}></div>
            </div>
            <div style={{justifyContent: "center", alignItems: "flex-start", display: "flex", gap: "2rem" }}>
                {/* wheel */}
                <div style={{ width: "300px", height: "300px", position: "relative" }}>
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
                        {list.map((item, index) => {
                            const rotate = index * degreesPerOption;
                            const startAngle = normalizeAngle(-degreesPerOption / 2);
                            const endAngle = normalizeAngle(degreesPerOption / 2);
                            const sectorColor = itemColors[index];

                            return (
                                <div
                                    key={index}
                                    style={{
                                        position: "absolute",
                                        width: "100%",
                                        height: "100%",
                                        borderRadius: "50%",
                                        transformOrigin: "center center",
                                        transform: `rotate(${rotate}deg)`,
                                        background: `conic-gradient(${sectorColor} 0deg, ${sectorColor} ${endAngle}deg, 
                                                    transparent ${endAngle}deg, transparent ${startAngle}deg, 
                                                    ${sectorColor} ${startAngle}deg`,
                                        display: "flex",
                                        alignItems: "center",
                                        justifyContent: "center",
                                        color: "white",
                                        fontSize: "30px"
                                    }}
                                >
                                    <span style={{
                                        position: "absolute",
                                        top: "10%",           // move the label upward to the 10% position
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
                        })}
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

                {/* input + button */}
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
