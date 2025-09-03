export interface StepDefinition {
    code: string;
    title: string;
    actor: string;
    description: string;
    dataFlow: {
      in: string[];
      out: string[];
    };
    api?: {
      method: 'GET' | 'POST' | 'PUT' | 'DELETE';
      path: string;
      sample?: string;
    };
  }

  const sampleBodies = {
    B1: JSON.stringify({
      name: "E2E Test Site - {timestamp}",
      address: "123 Test Street, Test City",
      start_date: "{today+30d}",
      end_date: "{today+120d}",
      requested_by_id: "{users.SAFETY_MANAGER.id}"
    }, null, 2),
    B2: JSON.stringify({
      approved_by_id: "{users.MANUFACTURER.id}"
    }, null, 2),
    C3: JSON.stringify({
      site_id: "{siteId}",
      crane_id: "{craneId}",
      safety_manager_id: "{users.SAFETY_MANAGER.id}",
      start_date: "{today+30d}",
      end_date: "{today+120d}"
    }, null, 2),
    D1: JSON.stringify({
      site_crane_id: "{assignmentId}",
      driver_id: "{users.DRIVER.id}",
      start_date: "{today+30d}",
      end_date: "{today+120d}"
    }, null, 2),
    D2: JSON.stringify({
      driver_assignment_id: "{driverAssignmentId}",
      work_date: "{today+30d}",
      check_in_at: "{today+30d}T08:00:00Z",
      check_out_at: "{today+30d}T17:00:00Z"
    }, null, 2),
    E1: JSON.stringify({
      site_id: "{siteId}",
      driver_id: "{users.DRIVER.id}",
      requested_by_id: "{users.SAFETY_MANAGER.id}",
      due_date: "{today+120d}"
    }, null, 2),
    E2: JSON.stringify({
      request_id: "{docRequestId}",
      doc_type: "Safety Certificate",
      file_url: "https://example.com/safety-cert.pdf"
    }, null, 2),
    E3: JSON.stringify({
      item_id: "{docItemId}",
      reviewer_id: "{users.SAFETY_MANAGER.id}",
      approve: true
    }, null, 2)
  };

  export const WORKFLOW_STEPS: StepDefinition[] = [
    {
      code: 'A1',
      title: '안전관리자 로그인',
      actor: 'SM',
      description: '안전관리자(Safety Manager) 역할로 로그인하여 인증 토큰을 확보한다.',
      dataFlow: { in: [], out: ['users.SAFETY_MANAGER'] },
      api: { method: 'POST', path: '/auth/login' },
    },
    {
      code: 'A2',
      title: '제조사 로그인',
      actor: 'MFR',
      description: '제조사(Manufacturer) 역할로 로그인하여 인증 토큰을 확보한다.',
      dataFlow: { in: [], out: ['users.MANUFACTURER'] },
      api: { method: 'POST', path: '/auth/login' },
    },
    {
      code: 'A3',
      title: '운전자 로그인',
      actor: 'DRV',
      description: '운전자(Driver) 역할로 로그인하여 인증 토큰을 확보한다.',
      dataFlow: { in: [], out: ['users.DRIVER'] },
      api: { method: 'POST', path: '/auth/login' },
    },
    {
      code: 'B1',
      title: '현장 생성 요청',
      actor: 'SM',
      description: '새 현장에 대한 “요청”을 제출한다. 직접 생성이 아닌 요청 기반 모델을 따른다.',
      dataFlow: { in: ['users.SAFETY_MANAGER'], out: ['siteId'] },
      api: { method: 'POST', path: '/org/sites', sample: sampleBodies.B1 },
    },
    {
      code: 'B2',
      title: '현장 요청 승인',
      actor: 'MFR',
      description: '접수된 현장 요청을 승인한다. 요청/현장 상태 전이는 원자적으로 처리된다는 가정하에, 결과만 컨텍스트에 반영한다.',
      dataFlow: { in: ['siteId', 'users.MANUFACTURER'], out: ['site.status'] },
      api: { method: 'PATCH', path: '/org/sites/{siteId}', sample: sampleBodies.B2 },
    },
    {
      code: 'C1',
      title: '사업주별 크레인 조회',
      actor: 'SM',
      description: '특정 사업주의 가용 크레인 목록을 조회한다. 이후 배치 요청에 필요한 식별자들을 확보한다.',
      dataFlow: { in: ['users.OWNER'], out: ['craneId'] },
      api: { method: 'GET', path: '/org/owners/{owner.orgId}/cranes' },
    },
    {
      code: 'C3',
      title: '크레인 현장 배치 ‘요청’ 생성',
      actor: 'SM',
      description: '가용 크레인 중 하나를 선택해 특정 현장으로의 배치를 요청한다(요청/승인 모델).',
      dataFlow: { in: ['siteId', 'craneId', 'users.SAFETY_MANAGER'], out: ['assignmentId'] },
      api: { method: 'POST', path: '/ops/crane-deployments', sample: sampleBodies.C3 },
    },
    {
      code: 'D1',
      title: '운전자 배정',
      actor: 'OWN',
      description: '배치된 크레인에 운전자를 배정한다.',
      dataFlow: { in: ['assignmentId', 'users.DRIVER'], out: ['driverAssignmentId'] },
      api: { method: 'POST', path: '/ops/driver-deployments', sample: sampleBodies.D1 },
    },
    {
      code: 'D2',
      title: '출근 체크-인',
      actor: 'DRV',
      description: '해당 현장/크레인에 출근 상태를 기록한다. 후속 서류 절차의 전제가 된다.',
      dataFlow: { in: ['driverAssignmentId'], out: ['attendance.latest'] },
      api: { method: 'POST', path: '/ops/driver-attendance-logs', sample: sampleBodies.D2 },
    },
    {
      code: 'E1',
      title: '서류 제출 요청',
      actor: 'SM',
      description: '특정 운전자에게 서류 제출을 요청한다.',
      dataFlow: { in: ['siteId', 'users.DRIVER', 'users.SAFETY_MANAGER'], out: ['docRequestId'] },
      api: { method: 'POST', path: '/compliance/document-requests', sample: sampleBodies.E1 },
    },
    {
      code: 'E2',
      title: '운전자 서류 제출',
      actor: 'DRV',
      description: '요청된 문서를 제출한다.',
      dataFlow: { in: ['docRequestId'], out: ['docItemId'] },
      api: { method: 'POST', path: '/compliance/document-items', sample: sampleBodies.E2 },
    },
    {
      code: 'E3',
      title: '서류 검토',
      actor: 'SM',
      description: '제출된 문서를 검토/확정한다.',
      dataFlow: { in: ['docItemId', 'users.SAFETY_MANAGER'], out: ['doc.reviewed'] },
      api: { method: 'POST', path: '/compliance/document-items/{docItemId}/review', sample: sampleBodies.E3 },
    },
    {
      code: 'F1',
      title: '워크플로우 집계',
      actor: 'SYSTEM',
      description: '사이트/크레인/요청/출근/서류 상태를 모아 전체 성공 여부를 요약한다.',
      dataFlow: { in: ['context'], out: ['snapshot.final'] },
    },
    {
      code: 'F2',
      title: '아티팩트 생성',
      actor: 'SYSTEM',
      description: '최종 JSON 스냅샷, 이벤트 로그, 화면 스냅샷 등 아티팩트를 생성/보관한다.',
      dataFlow: { in: ['snapshot.final'], out: ['artifacts.*'] },
    },
  ];
