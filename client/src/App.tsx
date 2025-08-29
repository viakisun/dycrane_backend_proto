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

type LogEntry = {
  type: 'info' | 'error' | 'success' | 'request' | 'response';
  message: string;
  data?: any;
};

function App() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [stepStatus, setStepStatus] = useState<Record<number, 'pending' | 'success' | 'error'>>({});

  const handleRunWorkflow = async () => {
    setIsRunning(true);
    setLogs([]);
    setStepStatus({});

    const workflowLogger = (message: string, data?: any) => {
        const type = message.startsWith('ERROR') ? 'error' : message.startsWith('STEP') ? 'info' : 'success';
        setLogs(prev => [...prev, { type, message, data }]);
    };

    await runWorkflow(workflowLogger, setStepStatus);
    setIsRunning(false);
  };

  const renderLogData = (data: any) => {
    if (typeof data !== 'string') {
        data = JSON.stringify(data, null, 2);
    }
    return <pre className="log-json">{data}</pre>;
  }

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
                <li key={index} className={stepStatus[index + 1] || 'pending'}>
                  {step}
                </li>
              ))}
            </ol>
          </div>
          <div className="log-output">
            <h2>Logs</h2>
            <div className="log-entries">
              {logs.map((log, index) => (
                <div key={index} className={`log-entry log-${log.type}`}>
                  <span className="log-message">{log.message}</span>
                  {log.data && renderLogData(log.data)}
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
