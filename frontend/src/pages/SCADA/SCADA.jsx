import { useEffect, useState ,useRef} from "react";
import {
  MdFactory,
  MdWarning,
  MdWifi,
  MdPrecisionManufacturing,
  MdSecurity,
} from "react-icons/md";

import { getLatestSCADA } from "../../services/scadaService";

function SCADA() {
  const [scadaData, setScadaData] = useState({});

  // ==================================================
  // LOAD LIVE SCADA DATA
  // ==================================================

  useEffect(() => {
    const loadSCADA = async () => {
      try {
        const data = await getLatestSCADA();

        console.log("SCADA DATA FROM API:", data);

        setScadaData(data);
      } catch (error) {
        console.error(
          "Failed to load SCADA data:",
          error
        );
      }
    };

    loadSCADA();

    const interval = setInterval(
      loadSCADA,
      2000
    );

    return () => clearInterval(interval);
  }, []);

  // ==================================================
  // MACHINE DATA
  // ==================================================

  const machines =
  scadaData.machines?.machines || [];

  // ==================================================
  // SENSOR DATA ONLY
  // ==================================================

  const sensorData = Object.entries(
    scadaData
  ).filter(
    ([key, data]) =>
      key !== "alarm" &&
      key !== "attack" &&
      key !== "machines" &&
      data?.sensor_type
  );

  // ==================================================
  // ALARM
  // ==================================================

  const activeAlarm =
    scadaData.alarm?.status === "ACTIVE";

  // ==================================================
  // ATTACK
  // ==================================================

  const attack = scadaData.attack;

const [attackElapsedTime, setAttackElapsedTime] = useState(0);

const attackStartTimeRef = useRef(null);
const attackIdRef = useRef(null);

useEffect(() => {
  if (!attack) {
    attackStartTimeRef.current = null;
    attackIdRef.current = null;
    setAttackElapsedTime(0);
    return;
  }

  if (attack.state === "RUNNING") {

    // Detect a new attack
    if (attackIdRef.current !== attack.attack_id) {
      attackIdRef.current = attack.attack_id;
      attackStartTimeRef.current = Date.now();
    }

    const updateElapsedTime = () => {
      if (!attackStartTimeRef.current) return;

      const elapsed = Math.floor(
        (Date.now() - attackStartTimeRef.current) / 1000
      );

      setAttackElapsedTime(
        Math.min(
          elapsed,
          attack.duration || elapsed
        )
      );
    };

    updateElapsedTime();

    const timer = setInterval(
      updateElapsedTime,
      1000
    );

    return () => clearInterval(timer);
  }

  // Attack stopped
  setAttackElapsedTime(
    attack.elapsed_time || 0
  );

}, [attack]);

const attackActive =
  attack?.state === "RUNNING";

  return (
    <div>

      {/* ==================================================
          HEADER
      ================================================== */}

      <div className="flex items-center justify-between mb-8">

        <div>
          <h1 className="text-3xl font-bold text-white">
            SCADA Monitor
          </h1>

          <p className="text-slate-400 mt-1">
            Industrial Control & Monitoring
          </p>
        </div>

        <div className="flex items-center gap-2 text-green-400">

          <MdWifi className="text-xl" />

          <span className="text-sm">
            Communication Online
          </span>

        </div>

      </div>


      {/* ==================================================
          FACTORY SUMMARY
          ================================================== */}

      <div className="grid grid-cols-4 gap-6 mb-8">

        {/* Factory */}

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">

          <div className="flex justify-between">

            <p className="text-slate-400">
              Factory
            </p>

            <MdFactory className="text-cyan-400 text-2xl" />

          </div>

          <h2 className="text-xl font-bold mt-3">
            LightX Smart Factory
          </h2>

          <p className="text-green-400 text-sm mt-2">
            OPERATIONAL
          </p>

        </div>


        {/* Production Line */}

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">

          <p className="text-slate-400">
            Production Line
          </p>

          <h2 className="text-xl font-bold mt-3">
            LINE-001
          </h2>

          <p className="text-green-400 text-sm mt-2">
            RUNNING
          </p>

        </div>


        {/* Machines */}

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">

          <p className="text-slate-400">
            Machines
          </p>

          <h2 className="text-3xl font-bold mt-3">
            6
          </h2>

          <p className="text-green-400 text-sm mt-2">
            All Operational
          </p>

        </div>


        {/* Active Alarms */}

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">

          <div className="flex justify-between">

            <p className="text-slate-400">
              Active Alarms
            </p>

            <MdWarning className="text-yellow-400 text-2xl" />

          </div>

          <h2 className="text-3xl font-bold mt-3">
            {activeAlarm ? 1 : 0}
          </h2>

          <p
            className={
              activeAlarm
                ? "text-red-400 text-sm mt-2"
                : "text-green-400 text-sm mt-2"
            }
          >
            {activeAlarm
              ? scadaData.alarm.message
              : "No Active Alarms"}
          </p>

        </div>

      </div>


      {/* ==================================================
          ATTACK STATUS
          ================================================== */}

      {attack && (

        <div
          className={`mb-8 rounded-xl border p-5 ${
            attackActive
              ? "bg-red-950/40 border-red-500"
              : "bg-slate-800 border-slate-700"
          }`}
        >

          <div className="flex items-center justify-between">

            <div className="flex items-center gap-3">

              <MdSecurity
                className={`text-2xl ${
                  attackActive
                    ? "text-red-400"
                    : "text-cyan-400"
                }`}
              />

              <div>

                <h2 className="text-lg font-semibold">
                  Attack Monitoring
                </h2>

                <p className="text-sm text-slate-400">
                  Cyber-attack state received from MQTT
                </p>

              </div>

            </div>


            <span
              className={`px-3 py-1 rounded-full text-sm font-semibold ${
                attackActive
                  ? "bg-red-500/20 text-red-400"
                  : "bg-green-500/20 text-green-400"
              }`}
            >
              {attack.state}
            </span>

          </div>


          <div className="grid grid-cols-4 gap-4 mt-5">

            <div>
              <p className="text-xs text-slate-500">
                Attack
              </p>

              <p className="font-semibold mt-1">
                {attack.attack_name}
              </p>
            </div>


            <div>
              <p className="text-xs text-slate-500">
                Type
              </p>

              <p className="font-semibold mt-1">
                {attack.type}
              </p>
            </div>


            <div>
              <p className="text-xs text-slate-500">
                Target Layer
              </p>

              <p className="font-semibold mt-1">
                {attack.target_layer}
              </p>
            </div>


            <div>
              <p className="text-xs text-slate-500">
                Duration
              </p>

              <p className="font-semibold mt-1">
                {attackElapsedTime}s /{" "}
                {attack.duration}s
              </p>
            </div>

          </div>

        </div>

      )}


      {/* ==================================================
          MACHINE OVERVIEW
          ================================================== */}

      <div className="bg-slate-900 border border-slate-700 rounded-xl p-6">

        <div className="flex items-center gap-3 mb-6">

          <MdPrecisionManufacturing className="text-cyan-400 text-2xl" />

          <div>

            <h2 className="text-xl font-semibold">
              Machine Overview
            </h2>

            <p className="text-sm text-slate-400">
              Production Line 1
            </p>

          </div>

        </div>


        <div className="grid grid-cols-3 gap-5">

          {machines.map((machine) => (

            <div
              key={machine.machine_code}
              className="bg-slate-800 border border-slate-700 rounded-xl p-5 hover:border-cyan-400 transition"
            >

              <div className="flex justify-between items-start">

                <div>

                  <h3 className="text-lg font-semibold">
                    {machine.name}
                  </h3>

                  <p className="text-sm text-slate-400">
                    {machine.machine_code}
                  </p>

                </div>

                <span className="flex items-center gap-2 text-green-400 text-sm">

                  <span className="w-2 h-2 rounded-full bg-green-400" />

                  {machine.state}

                </span>

              </div>


              <div className="mt-5">

                <div className="flex justify-between text-sm mb-2">

                  <span className="text-slate-400">
                    Health
                  </span>

                  <span>
                    {machine.health}%
                  </span>

                </div>


                <div className="w-full bg-slate-700 rounded-full h-2">

                  <div
                    className="bg-green-400 h-2 rounded-full"
                    style={{
                      width: `${machine.health}%`,
                    }}
                  />

                </div>

              </div>

            </div>

          ))}

        </div>

      </div>


      {/* ==================================================
          LIVE SCADA DATA
          ================================================== */}

      <div className="grid grid-cols-2 gap-6 mt-6">


        {/* Live Telemetry */}

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">

          <h2 className="text-lg font-semibold mb-4">
            Live Telemetry
          </h2>


          <div className="grid grid-cols-2 gap-4">

            {sensorData.map(
              ([sensor, data]) => (

                <div
                  key={sensor}
                  className="bg-slate-900 border border-slate-700 rounded-lg p-4"
                >

                  <p className="text-slate-400 text-sm capitalize">
                    {sensor}
                  </p>

                  <p className="text-xs text-slate-500 mt-1">
                    Sensor Code:{" "}
                    {data.sensor_code}
                  </p>

                  <p className="text-2xl font-bold text-cyan-400 mt-2">
                    {data.value}{" "}
                    {data.unit}
                  </p>

                  <p className="text-xs text-green-400 mt-2">
                    {data.status}
                  </p>

                  <p className="text-xs text-slate-500 mt-2">
                    MQTT: {data.topic}
                  </p>

                  <p className="text-xs text-slate-500 mt-1">
                    Last Update:{" "}
                    {data.timestamp}
                  </p>

                </div>

              )
            )}

          </div>

        </div>


        {/* ==================================================
            SCADA COMMUNICATION
            ================================================== */}

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">

          <h2 className="text-lg font-semibold mb-4">
            SCADA Communication
          </h2>


          <div className="space-y-3">

            <div className="flex justify-between">

              <span className="text-slate-400">
                MQTT Broker
              </span>

              <span className="text-green-400">
                ONLINE
              </span>

            </div>


            <div className="flex justify-between">

              <span className="text-slate-400">
                SCADA Backend
              </span>

              <span className="text-green-400">
                ONLINE
              </span>

            </div>


            <div className="flex justify-between">

              <span className="text-slate-400">
                Sensors Received
              </span>

              <span className="text-cyan-400">
                {sensorData.length}
              </span>

            </div>


            <div className="flex justify-between">

              <span className="text-slate-400">
                Attack Channel
              </span>

              <span className="text-green-400">
                ONLINE
              </span>

            </div>


            <div className="flex justify-between">

              <span className="text-slate-400">
                Attack State
              </span>

              <span
                className={
                  attackActive
                    ? "text-red-400"
                    : "text-green-400"
                }
              >
                {attack
                  ? attack.state
                  : "NONE"}
              </span>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default SCADA;