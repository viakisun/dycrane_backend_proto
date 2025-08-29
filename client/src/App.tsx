import React, { useState } from 'react';
import './style.css';

import { runWorkflow } from './workflow';

const STEPS = [
  "1. 사이트 생성 (Create Site)",
  "2. 사이트 승인 (Approve Site)",
  "3. 크레인 목록 조회 (List Cranes)",
  "4. 크레인 할당 (Assign Crane)",
  "5. 운전자 할당 (Assign Driver)",
  "6. 출석 기록 (Record Attendance)",
  "7. 문서 요청 (Request Document)",
  "8. 문서 제출 (Submit Document)",
  "9. 문서 검토 (Review Document)",
];

function App() {
  const [logs, setLogs] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const handleRunWorkflow = async () => {
    setIsRunning(true);
    setLogs(['Workflow started...']);
    const workflowLogger = (message: string) => {
      setLogs(prev => [...prev, message]);
    };
    await runWorkflow(workflowLogger);
    setIsRunning(false);
  };

  return (
    <div className="App">
      <header>
        <h1>DY Crane - E2E Test Client</h1>
        <p>A client to demonstrate and test the 9-step business workflow.</p>
      </header>
      <main>
        <div className="controls">
          <button onClick={handleRunWorkflow} disabled={isRunning}>
            {isRunning ? 'Running...' : 'Run Full Workflow'}
          </button>
        </div>
        <div className="workflow-container">
          <div className="steps-list">
            <h2>Workflow Steps</h2>
            <ol>
              {STEPS.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </div>
          <div className="log-output">
            <h2>Logs</h2>
            <pre>
              {logs.map((log, index) => (
                <div key={index}>{log}</div>
              ))}
            </pre>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
