# 🏛️ Chatbot Law 기술 문서 (Wiki)

**전세사기 피해자 법률 상담 AI 챗봇 (Chatbot Law – Production)** 프로젝트의 공식 기술 문서 및 운영 가이드입니다.  
본 위키는 서비스 아키텍처, 로컬 개발 환경 구축, 데이터베이스 마이그레이션, RAG 벡터 인덱싱, API 명세, 그리고 AWS 클라우드 배포 파이프라인에 대한 실무 지침을 상세히 다룹니다.

---

## 📌 문서 목차 (Quick Navigation)

| 카테고리 | 문서 링크 | 주요 내용 |
|:---|:---|:---|
| 🚀 **시작하기** | [[Local-Development]] | Python 3.11 백엔드, React 프론트엔드 로컬 실행 및 테스트 방법 |
| ⚙️ **환경 설정** | [[Environment-Variables]] | 로컬(`local`), 개발(`dev`), 운영(`prod`) 환경 변수 목록 및 Secret 관리 |
| 🗄️ **데이터베이스** | [[Database-Migration]] | PostgreSQL 스키마 구조, SQLAlchemy 모델 및 Alembic 마이그레이션 워크플로우 |
| 🔍 **AI & RAG** | [[Data-Indexing]] | 전세사기 특별법/임대차보호법 docx 데이터 전처리, 청킹, 임베딩 및 Pinecone 인덱싱 파이프라인 |
| 📡 **API 레퍼런스** | [[API-Documentation]] | 챗봇 질의응답, 대화 이력 조회/저장, 헬스체크 및 `X-Request-ID` 전역 추적 명세 |
| ☁️ **인프라 & 배포** | [[Deployment]] | AWS Elastic Beanstalk, S3, CloudFront CDN, OIDC 기반 GitHub Actions CI/CD 무중단 배포 |

---

## 🎯 개발 원칙 및 운영 기준선 (Engineering Baseline)

1. **Dev / Prod Parity (환경 일치성)**
   - 로컬 개발 환경과 실제 AWS 배포 환경 간의 기술 스택 차이를 최소화합니다.
   - 단일 원천 설정(`core/config.py`)을 통해 환경 변수 유효성을 시작 시점에 검증(Fail-Fast)합니다.

2. **Zero Hallucination RAG Pipeline**
   - 법률 도메인의 특수성을 고려하여 단순 유사도 검색에 그치지 않고, 조·항·호 단위 메타데이터와 결합된 결정론적 앙커 토큰(`⟦n⟧`) 인용 체계를 적용합니다.

3. **End-to-End Observability**
   - 브라우저 요청 발급 시부터 백엔드 API, DB 쿼리, LLM 체인 호출까지 `X-Request-ID`를 연속적으로 전파하여 장애 발생 시 즉각적인 원인 규명이 가능하도록 설계되었습니다.

---

> [!NOTE]
> 저장소 메인 소개 및 기능 요약은 [README.md](https://github.com/youneedpython/chatbot-law-production/blob/main/README.md)에서 확인하실 수 있습니다.
