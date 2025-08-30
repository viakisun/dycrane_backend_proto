import React, { useState } from 'react';
import { runWorkflow } from './workflow';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { motion, AnimatePresence } from 'framer-motion';
import GlitchText from './components/GlitchText';
import './components/Glitch.css';
import Particles from './components/Particles';
import './components/Particles.css';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const STEPS = [
  "1. Create Site",
  "2. Approve Site",
  "3. List Cranes",
  "4. Assign Crane",
  "5. Assign Driver",
  "6. Record Attendance",
  "7. Request Document",
  "8. Submit Document",
  "9. Review Document",
];

type LogEntry = {
  type: 'info' | 'error' | 'success' | 'request' | 'response';
  message: string;
  data?: any;
};

function App() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [stepStatus, setStepStatus] = useState<Record<number, 'pending' | 'success' | 'error'>>({});
  const [currentStep, setCurrentStep] = useState(0);
  const [error, setError] = useState<string | null>(null);


  const handleRunWorkflow = async () => {
    setIsRunning(true);
    setLogs([]);
    setStepStatus({});
    setCurrentStep(0);
    setError(null);

    const workflowLogger = (message: string, data?: any) => {
        const type = message.startsWith('ERROR') ? 'error' : message.startsWith('STEP') ? 'info' : 'success';
        if (type === 'error') {
          setError(message);
        }
        if (message.startsWith('STEP')) {
          const stepMatch = message.match(/STEP (\d+)/);
          if (stepMatch) {
            setCurrentStep(parseInt(stepMatch[1], 10));
          }
        }
        setLogs(prev => [...prev, { type, message, data }]);
    };

    await runWorkflow(workflowLogger, setStepStatus);
    setIsRunning(false);
    setCurrentStep(STEPS.length + 1); // Workflow finished
  };

  const renderLogData = (data: any) => {
    if (typeof data !== 'string') {
        data = JSON.stringify(data, null, 2);
    }
    return <pre className="bg-black bg-opacity-50 p-4 rounded-lg text-sm">{data}</pre>;
  }

  return (
    <div className="min-h-screen flex flex-col p-4 sm:p-6 lg:p-8">
      <Particles />
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 right-4 z-50"
          >
            <div className="bg-red-900/50 backdrop-blur-sm border border-red-500 text-red-300 px-6 py-4 rounded-lg shadow-neon-magenta">
              <p className="font-bold uppercase">System Alert</p>
              <p>{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <header className="mb-8 text-center">
        <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-cyan-glow uppercase tracking-widest" style={{ textShadow: '0 0 10px #00ffff' }}>
          DY Crane // E2E Test Client
        </h1>
        <p className="text-sm sm:text-base text-gray-400 mt-2">
          MISSION STATUS // WORKFLOW VALIDATION
        </p>
      </header>
      <main className="flex-grow grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-1">
          <div className="bg-black bg-opacity-30 p-6 rounded-lg border border-cyan-glow/20 h-full">
            <h2 className="text-xl font-bold text-cyan-glow mb-6 text-center uppercase tracking-widest">Workflow Steps</h2>
            <div className="relative">
              {/* Vertical line */}
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-cyan-glow/20" />

              {STEPS.map((step, index) => {
                const status = stepStatus[index + 1] || 'pending';
                const isCurrent = currentStep === index + 1;
                const isCompleted = status === 'success';
                const isFailed = status === 'error';

                return (
                  <div key={index} className="flex items-center mb-4 last:mb-0">
                    <div className="relative z-10">
                      <div className={cn(
                        "w-8 h-8 rounded-full flex items-center justify-center border-2",
                        {
                          "border-cyan-glow bg-cyan-900 animate-pulse": isCurrent,
                          "border-green-500 bg-green-900": isCompleted,
                          "border-red-500 bg-red-900 animate-ping": isFailed,
                          "border-gray-600 bg-gray-800": status === 'pending'
                        }
                      )}>
                        <span className="text-sm font-bold">{index + 1}</span>
                      </div>
                    </div>
                    <span className={cn(
                      "ml-4 text-sm font-medium",
                      {
                        "text-cyan-glow": isCurrent,
                        "text-green-400": isCompleted,
                        "text-red-400": isFailed,
                        "text-gray-400": status === 'pending'
                      }
                    )}>
                      {step}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
        <div className="lg:col-span-3 flex flex-col gap-8">
          <div className="text-center">
            <button
              onClick={handleRunWorkflow}
              disabled={isRunning}
              className={cn(
                "px-8 py-4 text-lg font-bold uppercase tracking-widest text-white transition-all duration-300 rounded-lg",
                "bg-cyan-600 hover:bg-cyan-500 disabled:bg-gray-700 disabled:cursor-not-allowed",
                "shadow-lg shadow-cyan-500/20 hover:shadow-xl hover:shadow-cyan-500/40",
                "transform hover:-translate-y-1",
                {"animate-pulse": !isRunning}
              )}
            >
              {isRunning ? 'Executing Workflow...' : 'Initiate Full Workflow'}
            </button>
          </div>
          <div className="bg-black bg-opacity-30 p-6 rounded-lg border border-cyan-glow/20 flex-grow">
            <h2 className="text-xl font-bold text-cyan-glow mb-6 text-center uppercase tracking-widest">Real-Time Logs</h2>
            <div className="h-96 overflow-y-auto p-4 bg-black bg-opacity-50 rounded-lg border border-gray-700">
              {logs.map((log, index) => (
                <div key={index} className={cn("flex items-start mb-2", {
                  'text-red-400': log.type === 'error',
                  'text-green-400': log.type === 'success',
                  'text-gray-400': log.type === 'info',
                })}>
                  <span className="mr-2 font-bold">{`> `}</span>
                  <div className="flex-1">
                    <GlitchText text={log.message} />
                    {log.data && (
                      <div className="mt-1">
                        {renderLogData(log.data)}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
