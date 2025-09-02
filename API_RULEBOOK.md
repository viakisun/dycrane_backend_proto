# API 네이밍 & 설계 규칙서
*버전 1.0 — API 디자인 오피스 작성*

---

## 1. 개요
본 문서는 시스템 내 모든 RESTful API의 **네이밍, 버전 관리, 설계 원칙**을 정의한다.  
목표는 **일관성, 명확성, 확장성**을 확보하여 엔드포인트 의미의 모호성을 제거하고, 장기적인 유지보수를 위한 기반을 마련하는 것이다.

---

## 2. 버전 관리
- 모든 엔드포인트는 **버전 접두어**를 반드시 포함해야 한다.  
  ```
  /api/v1/...
  ```
- 필요성:
  - 다중 API 세대의 **병행 지원** 가능
  - 외부 클라이언트에게 **명확한 업그레이드 경로** 제공
- 향후 `/api/v2`, `/api/v3`는 **호환성이 깨지는 변경**이 있을 때만 도입한다.

---

## 3. 컨텍스트 네임스페이스
루트 경로가 혼잡해지는 것을 방지하고 도메인별 구분을 명확히 하기 위해, 엔드포인트는 다음과 같이 **네임스페이스**로 구분한다.

| 컨텍스트      | 목적                                   | 예시                                   |
|---------------|----------------------------------------|----------------------------------------|
| `system`      | 헬스체크, 운영 도구                   | `/api/v1/system/health`                |
| `catalog`     | 참조/레퍼런스 데이터                  | `/api/v1/catalog/crane-models`         |
| `org`         | 조직, 현장, 자산 관리                 | `/api/v1/org/sites`                    |
| `ops`         | 운영 실행(배치, 출석, 편성 등)        | `/api/v1/ops/crane-deployments`        |
| `compliance`  | 문서 요청, 제출, 심사                 | `/api/v1/compliance/document-items`    |
| `deploy`      | 일반 요청, 배포 워크플로우            | `/api/v1/deploy/requests`              |

---

## 4. 리소스 네이밍 규칙
- 리소스는 **복수형(kebab-case)** 을 사용한다.  
  - ✅ `/driver-attendance-logs`  
  - ❌ `/driverAttendance`
- Path 파라미터는 **camelCase**를 사용한다.  
  - ✅ `/owners/{ownerId}/cranes`  
  - ❌ `/owners/{owner_id}/cranes`
- 모호한 단어(`attendance`, `assignment`)는 지양하고 **도메인 명확화**를 한다.  
  - `driver-attendance-logs` (운전자의 출석 기록)  
  - `crane-deployments`, `driver-deployments` (현장 배치)  
  - `driver-rosters` (근무 편성)  
  - `crane-ownerships` (소유 관계)

---

## 5. HTTP 메서드 사용 규칙
### 5.1 메서드 의미
- `GET` → 조회  
- `POST` → 새 리소스 생성 / **액션(행위, 상태 전이)** 수행  
- `PATCH` → 기존 리소스 속성 일부 수정  
- `PUT` → 리소스 전체 교체 (필요한 경우에만)  
- `DELETE` → 리소스 삭제  

### 5.2 PATCH vs POST 구분
- **속성 수정** → `PATCH`  
  - 예: 사이트 이름 변경  
  - `PATCH /api/v1/org/sites/{siteId}`
- **상태 전이 / 명시적 행위** → `POST`  
  - 예: 문서 승인/반려  
  - `POST /api/v1/compliance/document-items/{itemId}/review`

---

## 6. 액션 엔드포인트
행위는 반드시 **명시적 액션 엔드포인트**로 분리한다.  
- ✅ `/document-items/{id}/review` (승인/반려)  
- ✅ `/driver-attendance-logs/{id}/check-in`  
- ✅ `/crane-deployments/{id}/terminate`  
- ❌ `PATCH /document-items/{id}` + `approve: true`

응답 규칙:  
- **상태 변경** → `200 OK`  
- **새 기록 생성(예: review 로그)** → `201 Created`

---

## 7. 쿼리 파라미터 규칙
- **페이징**: `limit`, `offset` (또는 `page[size]`, `page[number]`)  
- **필터링**: `filter[siteId]=...`, `filter[driverId]=...`  
- **정렬**: `sort=createdAt,-name`  
- **기간**: `{ "start": "ISO8601", "end": "ISO8601" }`

---

## 8. 에러 처리 규칙
- `422` → 유효성 오류  
- `403` → 권한 없음  
- `404` → 리소스 없음  
- `409` → 충돌(중복, 점유, 규칙 위반)  
- `500` → 서버 내부 오류  

에러 응답은 **표준 JSON 스키마**(예: JSON:API Error Objects)를 따른다.

---

## 9. Operation ID & Tagging
- **operationId**: `{context}.{resource}.{verb}`  
  - 예: `ops.driverAttendanceLogs.checkIn`
- **tags**: 컨텍스트 단위(`System`, `Catalog`, `Org`, `Ops`, `Compliance`, `Deploy`)

---

## 10. 엔드포인트 매핑 (현재 → 변경안)

### System
- `GET /api/health/` → `GET /api/v1/system/health`  
- `POST /api/health/reset-transactional` → `POST /api/v1/system/tools/reset-transactional`  
- `POST /api/health/reset-full` → `POST /api/v1/system/tools/reset-full`  

### Catalog
- `GET /api/crane-models/` → `GET /api/v1/catalog/crane-models`  

### Org
- `GET /api/sites/` → `GET /api/v1/org/sites`  
- `POST /api/sites/` → `POST /api/v1/org/sites`  
- `GET /api/cranes/` → `GET /api/v1/org/cranes`  
- `GET /api/owners/with-stats` → `GET /api/v1/org/owners?include=stats`  
- `GET /api/owners/{owner_id}/cranes` → `GET /api/v1/org/owners/{ownerId}/cranes`  

### Ops
- `POST /api/crane-assignments/` → `POST /api/v1/ops/crane-deployments`  
- `POST /api/driver-assignments/` → `POST /api/v1/ops/driver-deployments`  
- `POST /api/attendances/` → `POST /api/v1/ops/driver-attendance-logs`  

### Compliance
- `POST /api/document-requests/` → `POST /api/v1/compliance/document-requests`  
- `POST /api/document-items/` → `POST /api/v1/compliance/document-items`  
- `PATCH /api/document-items/{item_id}` → `POST /api/v1/compliance/document-items/{itemId}/review`  

### Deploy
- `POST /api/requests/` → `POST /api/v1/deploy/requests`  
- `POST /api/requests/{request_id}/respond` → `POST /api/v1/deploy/requests/{requestId}/responses`  

---

## 11. 마이그레이션 지침
1. **폐기 정책**  
   - 기존 엔드포인트는 OpenAPI에서 `deprecated: true` 표시  
   - `x-replaced-by` 확장 필드로 신규 엔드포인트를 명시  

2. **게이트웨이 리라이트**  
   - API Gateway에서 old → new 경로 자동 매핑 지원  

3. **공존 기간**  
   - 최소 **90일 이상** 구버전 유지  
   - **깨지는 변경**의 경우 **180일 전 사전 공지**  

4. **변경 로그**  
   - 모든 릴리스에 마이그레이션 가이드 및 예제 요청/응답 포함  

---

## 12. 결론
이 규칙서는 다음을 보장한다.  
- **명확성**: `attendance`, `assignment`와 같은 모호 단어 제거  
- **일관성**: 네이밍, 액션, 버전 정책 통일  
- **확장성**: 컨텍스트 기반 구조로 장기 확장 대비  
- **신뢰성**: 외부 파트너가 의존할 수 있는 안정된 계약 제공  

이 원칙을 준수하면 API는 **예측 가능성, 감사 용이성, 장기적 유지보수성**을 확보할 수 있다.  
