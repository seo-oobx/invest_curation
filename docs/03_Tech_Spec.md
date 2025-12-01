# 03. 기술 명세서 (Tech Spec)

## 1. 기술 스택 (Tech Stack)
* **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, Recharts (차트 라이브러리).
* **Backend:** Python FastAPI (REST API, 비동기 처리).
* **Database & Auth:** Supabase (PostgreSQL, Authentication).
* **Crawler:** Python Playwright (Headless Browser), BeautifulSoup4.
* **Infrastructure:** Vercel (Frontend), Google Cloud Run (Backend), Supabase Cloud (DB).

## 2. 시스템 아키텍처
[Client (Next.js)] <--> [API Gateway (FastAPI)] <--> [Supabase (DB/Auth)]
                                      ^
                                      |
                            [Crawler / Scheduler]
                            (Daily Job: Naver DataLab, News, YouTube)

## 3. 데이터베이스 스키마 (Supabase PostgreSQL)

### `users`
* `id` (UUID, PK): Supabase Auth 연동
* `membership_tier` (TEXT): 'FREE', 'PRO'
* `created_at` (TIMESTAMPTZ)

### `events`
* `id` (BIGINT, PK)
* `title` (TEXT)
* `target_date` (DATE): D-Day
* `is_date_confirmed` (BOOLEAN)
* `event_type` (TEXT): 'TYPE_A', 'TYPE_B'
* `hype_score` (INT): 현재 Hype 점수
* `related_tickers` (TEXT[]): 관련 종목 코드 배열 (ex: ['005930', '000660'])
* `status` (TEXT): 'ACTIVE', 'FINISHED'

### `hype_metrics` (시계열 데이터)
* `id` (BIGINT, PK)
* `event_id` (FK -> events.id)
* `recorded_at` (DATE)
* `search_volume` (INT)
* `community_buzz` (INT)
* `youtube_count` (INT)

### `event_proxies` (선행 시그널)
* `id` (BIGINT, PK)
* `parent_event_id` (FK -> events.id)
* `proxy_name` (TEXT)
* `detected_at` (TIMESTAMPTZ)

## 4. API Endpoints (Core)
* `GET /api/v1/events`: 이벤트 목록 조회 (필터: sort=hype/date, category).
* `GET /api/v1/events/{id}`: 이벤트 상세 및 차트 데이터 조회.
* `GET /api/v1/events/{id}/stocks`: 관련 종목 주가 및 Valuation 조회.
* `POST /api/v1/crawl/trigger`: (Admin) 크롤러 수동 실행 트리거.