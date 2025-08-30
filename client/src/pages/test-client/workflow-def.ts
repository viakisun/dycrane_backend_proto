export const WORKFLOW_STEPS = [
  {
    code: 'A1',
    title: '역할별 로그인/세션 준비',
    actor: 'SM, MFR, OWN, DRV',
    description: '시나리오 전 단계에서 사용할 인증/세션을 준비한다. 역할별 토큰과 최소 프로필을 확보하고, 이후 단계들이 공통 컨텍스트를 통해 참조할 수 있게 한다.',
    dataFlow: {
      in: [],
      out: ['tokens.*', 'users.*'],
    },
  },
  {
    code: 'A2',
    title: '환경/스키마 확인',
    actor: 'SYSTEM',
    description: '서비스 가용성, 스키마/뷰/인덱스 존재 여부를 사전 점검한다. 부족한 항목은 서버/DB 보강 작업 목록으로만 기록한다(즉시 수정 금지).',
    dataFlow: {
      in: [],
      out: ['env.checklist'],
    },
  },
  {
    code: 'B1',
    title: '현장 생성 요청',
    actor: 'SM',
    description: '새 현장에 대한 “요청”을 제출한다. 직접 생성이 아닌 요청 기반 모델을 따른다.',
    dataFlow: {
      in: ['users.SAFETY_MANAGER'],
      out: ['site.siteId', 'site.requestId'],
    },
  },
  {
    code: 'B2',
    title: '현장 요청 승인',
    actor: 'MFR',
    description: '접수된 현장 요청을 승인한다. 요청/현장 상태 전이는 원자적으로 처리된다는 가정하에, 결과만 컨텍스트에 반영한다.',
    dataFlow: {
      in: ['site.siteId', 'users.MANUFACTURER'],
      out: ['site.status'],
    },
  },
  {
    code: 'B3',
    title: '내 현장 확인',
    actor: 'SM',
    description: '승인된 현장이 목록에 반영되었는지 확인한다. 이후 배치/서류 단계에서 참조할 기준이 된다.',
    dataFlow: {
      in: ['users.SAFETY_MANAGER'],
      out: ['site.list'],
    },
  },
  {
    code: 'C1',
    title: '사업주 목록(통계)',
    actor: 'SM',
    description: '사업주 카드 목록과 가용/전체 크레인 수를 확인한다. 배치 대상 선택의 출발점이 된다.',
    dataFlow: {
      in: [],
      out: ['owners[]'],
    },
  },
  {
    code: 'C2',
    title: '사업주별 크레인(가용 필터)',
    actor: 'SM',
    description: '선택한 사업주의 가용 크레인 목록을 조회한다. 이후 배치 요청에 필요한 식별자들을 확보한다.',
    dataFlow: {
      in: ['owners[0].id'],
      out: ['cranes.byOwner[ownerId].available[]'],
    },
  },
  {
    code: 'C3',
    title: '크레인 현장 배치 ‘요청’ 생성',
    actor: 'SM',
    description: '가용 크레인 중 하나를 선택해 특정 현장으로의 배치를 요청한다(요청/승인 모델).',
    dataFlow: {
      in: ['site.siteId', 'cranes.byOwner[ownerId].available[0].id', 'users.SAFETY_MANAGER'],
      out: ['deploy.requestId'],
    },
  },
  {
    code: 'C4',
    title: '사업주의 요청함 확인',
    actor: 'OWN',
    description: '본인에게 들어온 크레인 배치 요청 목록을 확인한다.',
    dataFlow: {
      in: ['users.OWNER'],
      out: ['owner.pendingRequests[]'],
    },
  },
  {
    code: 'C5',
    title: '배치 요청 승인/거절',
    actor: 'OWN',
    description: '요청을 승인하거나 거절한다. 승인 시 크레인/사이트의 상태 전이가 발생한다는 전제를 따른다.',
    dataFlow: {
      in: ['owner.pendingRequests[0].id', 'users.OWNER'],
      out: ['deploy.status', 'crane.assigned', 'site.status'],
    },
  },
  {
    code: 'C6',
    title: '배치 결과 검증(현장 기준)',
    actor: 'SM',
    description: '대상 현장에 크레인이 배치되었는지 확인한다. 이후 운전자 시나리오의 전제가 된다.',
    dataFlow: {
      in: ['site.siteId'],
      out: ['site.assignedCranes[]'],
    },
  },
  {
    code: 'D1',
    title: '운전자 배정 확인',
    actor: 'DRV',
    description: '본인에게 배정된 크레인/현장을 조회한다. 출근 가능 조건을 확인한다.',
    dataFlow: {
      in: ['users.DRIVER'],
      out: ['driver.assigned[]'],
    },
  },
  {
    code: 'D2',
    title: '출근 체크-인',
    actor: 'DRV',
    description: '해당 현장/크레인에 출근 상태를 기록한다. 후속 서류 절차의 전제가 된다.',
    dataFlow: {
      in: ['driver.assigned[0].id'],
      out: ['attendance.latest'],
    },
  },
  {
    code: 'E1',
    title: '서류 제출 요청',
    actor: 'SM',
    description: '특정 운전자에게 서류 제출을 요청한다.',
    dataFlow: {
      in: ['site.siteId', 'users.DRIVER', 'users.SAFETY_MANAGER'],
      out: ['doc.request.documentId'],
    },
  },
  {
    code: 'E2',
    title: '운전자 서류 제출',
    actor: 'DRV',
    description: '요청된 문서를 제출한다.',
    dataFlow: {
      in: ['doc.request.documentId', 'users.DRIVER'],
      out: ['doc.submitted'],
    },
  },
  {
    code: 'E3',
    title: '서류 검토',
    actor: 'SM',
    description: '제출된 문서를 검토/확정한다.',
    dataFlow: {
      in: ['doc.submitted.id', 'users.SAFETY_MANAGER'],
      out: ['doc.reviewed'],
    },
  },
  {
    code: 'F1',
    title: '워크플로우 집계',
    actor: 'SYSTEM',
    description: '사이트/크레인/요청/출근/서류 상태를 모아 전체 성공 여부를 요약한다.',
    dataFlow: {
      in: ['context'],
      out: ['snapshot.final'],
    },
  },
  {
    code: 'F2',
    title: '아티팩트 생성',
    actor: 'SYSTEM',
    description: '최종 JSON 스냅샷, 이벤트 로그, 화면 스냅샷 등 아티팩트를 생성/보관한다.',
    dataFlow: {
      in: ['snapshot.final'],
      out: ['artifacts.*'],
    },
  },
];
