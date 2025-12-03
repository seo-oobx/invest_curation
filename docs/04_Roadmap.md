# 04. 개발 로드맵 및 액션 플랜 (Development Roadmap)

이 문서는 Alpha Calendar 프로젝트의 개발 진행 상황을 추적하고 관리하기 위한 살아있는 문서입니다.
각 단계가 완료될 때마다 체크박스(`[x]`)를 표시하여 진행률을 관리합니다.

## 🗓️ Phase 1: Foundation & Core API (Backend Focus)
**목표:** 데이터베이스 스키마를 확립하고, 이벤트를 조회/생성할 수 있는 핵심 API를 구축합니다.

- [x] **1.1 Database Schema (Supabase/PostgreSQL)**
    - [x] `users` 테이블 정의 (Auth 연동) -> [`api/app/db/schema.sql`](../api/app/db/schema.sql)
    - [x] `events` 테이블 정의 (핵심 데이터) -> [`api/app/db/schema.sql`](../api/app/db/schema.sql)
    - [x] `hype_metrics` 테이블 정의 (시계열 데이터) -> [`api/app/db/schema.sql`](../api/app/db/schema.sql)
    - [x] `event_proxies` 테이블 정의 (시그널) -> [`api/app/db/schema.sql`](../api/app/db/schema.sql)
    - [x] SQL 스크립트 작성 -> [`api/app/db/schema.sql`](../api/app/db/schema.sql)

- [x] **1.2 API Basic Setup (FastAPI)**
    - [x] FastAPI 프로젝트 구조 생성 -> [`api/`](../api/)
    - [x] 필수 패키지 설치 -> [`api/requirements.txt`](../api/requirements.txt)
    - [x] 환경 변수 설정 -> [`api/.env.example`](../api/.env.example), [`api/app/core/config.py`](../api/app/core/config.py)
    - [x] Supabase 클라이언트 연동 -> [`api/app/db/session.py`](../api/app/db/session.py)

- [x] **1.3 Core Logic & Endpoints**
    - [x] Pydantic Models 정의 -> [`api/app/schemas/event.py`](../api/app/schemas/event.py)
    - [x] `GET /events` (목록 조회) 구현 -> [`api/app/api/endpoints/events.py`](../api/app/api/endpoints/events.py)
    - [x] `GET /events/{id}` (상세 조회) 구현 -> [`api/app/api/endpoints/events.py`](../api/app/api/endpoints/events.py)
    - [x] `POST /events` (이벤트 생성) 구현 -> [`api/app/api/endpoints/events.py`](../api/app/api/endpoints/events.py)

---

## ⚙️ Phase 2: Data Pipeline & Logic (The "Alpha" Engine)
**목표:** 데이터 수집을 자동화하고, 수집된 데이터를 바탕으로 Hype Score를 계산하는 로직을 구현합니다.

- [x] **2.1 Crawler Engine (Playwright)**
    - [x] 크롤러 기본 구조 설계 -> [`api/app/services/crawler/base.py`](../api/app/services/crawler/base.py)
    - [x] **Type A (Fact)** 수집기 구현 (DART, 뉴스) -> [`api/app/services/crawler/type_a_news.py`](../api/app/services/crawler/type_a_news.py)
    - [x] **Type B (Hype)** 수집기 구현 (네이버 데이터랩, 커뮤니티) -> [`api/app/services/crawler/type_b_hype.py`](../api/app/services/crawler/type_b_hype.py)

- [x] **2.2 Hype Scoring Algorithm**
    - [x] `HypeCalculator` 서비스 클래스 구현 -> [`api/app/services/hype_calculator.py`](../api/app/services/hype_calculator.py)
    - [x] 검색량/커뮤니티 글 수 정규화(Normalization) 로직 -> [`api/app/services/hype_calculator.py`](../api/app/services/hype_calculator.py)
    - [x] 기울기(Slope) 기반 급상승 감지 로직 -> [`api/app/services/hype_calculator.py`](../api/app/services/hype_calculator.py)

- [ ] **2.3 Scheduler**
    - [ ] APScheduler 설정 (Daily Job)
    - [ ] 크롤링 -> 스코어링 -> DB 업데이트 파이프라인 연결

---

## 🖥️ Phase 3: Frontend MVP (Web)
**목표:** 사용자가 정보를 시각적으로 소비할 수 있는 웹 인터페이스를 구축합니다.

- [x] **3.1 Project Initialization**
    - [x] Next.js (App Router) 프로젝트 생성 (`web/`) -> [`web/`](../web/)
    - [x] Tailwind CSS & UI 라이브러리(Shadcn 등) 설정 -> [`web/components.json`](../web/components.json)

- [x] **3.2 Dashboard (Curator View)**
    - [x] API 연동 (`lib/api.ts`) -> [`web/src/lib/api.ts`](../web/src/lib/api.ts)
    - [x] 이벤트 카드 컴포넌트 구현 -> [`web/src/components/event-card.tsx`](../web/src/components/event-card.tsx)
    - [x] 메인 그리드 레이아웃 구현 (Hype Score 순 정렬) -> [`web/src/app/page.tsx`](../web/src/app/page.tsx)

- [x] **3.3 Detail Page (Analyst View)**
    - [x] 상세 정보 뷰 구현 -> [`web/src/app/events/[id]/page.tsx`](../web/src/app/events/[id]/page.tsx)
    - [x] Recharts 차트 연동 (Hype Chart) -> [`web/src/components/hype-chart.tsx`](../web/src/components/hype-chart.tsx)
    - [x] 관련 종목(Related Stocks) 리스트 구현 -> [`web/src/app/events/[id]/page.tsx`](../web/src/app/events/[id]/page.tsx)

---

## 🚀 Phase 4: Advanced Features & Polish
**목표:** 사용자 경험을 완성하고 운영 효율성을 높입니다.

- [ ] **4.1 Authentication (Google Login)**
    - [x] Supabase Auth 설정 가이드 (Google Cloud Console)
    - [x] Frontend: 로그인 버튼 및 세션 관리 (`web/src/components/auth/*`) -> [`web/src/components/auth/login-button.tsx`](../web/src/components/auth/login-button.tsx)
    - [ ] Backend: JWT 검증 미들웨어 (선택 사항)

- [ ] **4.2 Alert System**
    - [x] 알림 설정 UI (종버튼) -> [`web/src/components/event-card.tsx`](../web/src/components/event-card.tsx)
    - [x] Email 연동 (Resend) -> [`api/app/services/email_service.py`](../api/app/services/email_service.py)
    - [ ] **[TODO]** Resend 도메인 인증 (실제 서비스 배포 전 필수)

- [ ] **4.3 Admin Page**
    - [x] 관리자 대시보드 및 이벤트 생성 폼 -> [`web/src/app/admin/page.tsx`](../web/src/app/admin/page.tsx)
    - [ ] 크롤링 데이터 검수 및 승인 페이지
    - [ ] Hype Score 수동 보정 기능

---

## ☁️ Phase 5: Deployment & DevOps
**목표:** 서비스를 실제 환경에 배포하고 안정적으로 운영합니다.

- [x] **5.1 Backend Deployment (Railway)**
    - [x] Railway 프로젝트 설정 및 배포 완료
    - [x] 환경 변수 설정 (Supabase URL, API Keys)

- [x] **5.2 Frontend Deployment (Vercel)**
    - [x] Vercel 프로젝트 설정 및 배포 완료
    - [x] Backend API 연동 (Environment Variables)

- [x] **5.3 Integration**
    - [x] Vercel <-> Railway 통신 확인 (CORS, API URL)
