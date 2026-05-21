# JUST Long-Slit ICS 2.0 软件开发战略

```text
文档日期: 2026-05-21
建议文件名: docs/ics2_software_development_strategy.md
版本: v2026.05.21-r1
状态: Phase 2.8/v7 UI IA cleanup merged; Phase 2.9 Contract Hardening starts from durable Setup/Data Context
适用范围: JUST 长缝光谱仪 ICS 2.0 软件主线开发
```

## 1. 战略定位

JUST Long-Slit ICS 2.0 是 JUST 长缝光谱仪的软件控制骨架。它的定位不是“一个网页 GUI”，也不是“单个硬件驱动程序”，而是位于观测控制、望远镜状态、仪器机构、探测器、定标系统、数据产品之间的仪器控制系统。

当前主线已经明确：项目采用 simulation-first、API-first、分层架构、操作可审计、前端渐进迁移、后续真实硬件集成的路线。Phase 2.8/v7 UI IA cleanup 已合并到 `main`，`/ui` 默认进入 v7.1 operator-console prototype，v5 作为 fallback 保留。

ICS 2.0 的长期目标是：

```text
让 OCS / operator / future scripts 能以统一、可审计、可恢复的方式提交观测意图；
让 ICS 将观测意图转化为安全的仪器动作、状态机流转和数据产品记录；
让真实硬件接入之前，模拟链路已经具备可验证的端到端控制语义；
让真实硬件接入之后，系统仍然保持清晰边界、可回退、可诊断、可扩展。
```

## 2. 软件边界

### 2.1 ICS 负责什么

ICS 2.0 应负责：

```text
- 暴露稳定的 /api/v1/* 控制与状态接口；
- 维护仪器状态、曝光状态、子系统状态和 latest_job / request_id 审计链；
- 管理 setup/session context、slit、calibration、detector、presets、observation 等仪器控制语义；
- 提供 operator console，用于 routine observing、diagnostics、future engineer views；
- 通过 adapter/driver 边界接入模拟硬件与未来真实硬件；
- 将观测动作、观测结果、数据产品元数据和错误记录统一表达；
- 为 OCS、TCS、data product、quicklook、sequence runner、真实硬件集成预留合同。
```

### 2.2 ICS 不负责什么

ICS 2.0 不应越界承担以下职责：

```text
- 不负责改变光谱仪的光学分辨率本身；
- 不负责替代 OCS scheduler 或完整观测计划系统；
- 不负责替代 TCS 控制望远镜、调焦、转台、圆顶、天气权限等；
- 不负责在 routine operator UI 中暴露底层总线、PLC、motion-controller 或厂商 SDK 级控制；
- 不负责完整科学数据处理和光谱归约；
- 不负责在无硬件环境下伪造真实硬件 telemetry；
- 不负责把 placeholder 包装成 production capability。
```

例如，`R >= 1000 @ 1 arcsec`、可调分辨率、波长覆盖、线性色散等是光学和仪器设计约束。软件可以记录配置、校验状态、保存 FITS header、触发定标、辅助 QA，但软件本身不能“实现”光谱分辨率。

底层硬件通信协议不在当前软件阶段预先指定。真实硬件未来可能使用串口、USB、以太网、厂商 SDK、PLC/fieldbus、EPICS IOC 或其他控制接口；ICS 2.0 的战略目标是保留 adapter/gateway 边界，而不是提前把任何具体协议写成路线图主轴。

## 3. 架构护栏

后续每个 phase、PR、commit 都应通过以下检查：

| 护栏 | 判断问题 | 目的 |
|---|---|---|
| Contract first | 这个改动是在稳定领域/API 合同，还是只是在堆 UI/实现细节？ | 防止 UI 先行导致后端语义混乱 |
| Simulation parity | 真实硬件未来接入时，sim 路径还能保持同一合同吗？ | 防止 real-only hack |
| No telescope overreach | 是否越过 OCS/TCS 控制 pointing、rotator、guiding、offset、dome、weather authority？ | 防止 ICS 越界 |
| No fake capability | 是否把 placeholder 包装成真实能力？ | 防止现场使用时误判 |
| Auditable lifecycle | 高影响操作是否有 request_id、latest_job、result、error？ | 防止不可追踪操作 |
| Layer boundary | domain/application/kernel/api/ui/adapter 是否各司其职？ | 防止代码后期无法维护 |

## 4. 技术采纳门槛

任何新技术、协议、数据库、消息系统、实时框架、硬件总线、外部平台进入主路线图前，必须通过 Technology Adoption Gate。

```text
1. 它解决的当前项目问题是什么？
2. 这个问题是否已经在当前 phase 出现？
3. 是否有真实硬件、真实运维、真实接口合同支撑？
4. 是否可以先用更简单的 schema / simulator / file contract / adapter 解决？
5. 是否破坏当前 Domain / Kernel / Application / Adapter 分层？
6. 是否会让 routine operator UI 暴露底层工程复杂度？
7. 是否能被 pytest 或 integration test 覆盖？
8. 如果不用它，当前 phase 是否仍可推进？
```

判定规则：

```text
- 如果第 2、3、7 项不能回答清楚，不进入当前 phase。
- 如果只是未来可能需要，写成 TBD 或 candidate。
- 如果只是底层实现可能性，写成 adapter/gateway boundary。
- 战略文档优先写能力合同，不预设实现技术。
```

这条规则适用于硬件总线，也适用于 WebSocket、FITS writer、SQLite/session persistence、Prometheus、权限系统、自动恢复、复杂 detector write UI 等可能过早引入的技术点。

## 5. 当前主线基线

### 5.1 路由和 UI 基线

当前主线 UI 路由为：

```text
/ui        -> v7.1 default operator-console prototype
/ui/v7     -> v7.1 explicit operator-console prototype
/ui/v5     -> v5 stable legacy fallback
/ui/legacy -> v5 stable legacy fallback alias
/ui/v6     -> v6 operational-status review shell
```

v7.1 当前信息架构为：

```text
Setup
Instrument / Configure
Observe
Presets
Diagnostics
Housekeeping
Engineer
```

核心原则是：

```text
HTML owns durable structure.
Runtime JS enhances durable HTML skeletons.
```

v7 static shell cleanup 后，`ui_operational_v7.html` 是 `/ui` 与 `/ui/v7` 的 served layout source；runtime JS 保持 opt-in，不应创建与 HTML shell 竞争的重复 UI 面板。

### 5.2 后端 API 基线

当前 backend 以 `/api/v1/*` 为主线，主要接口包括：

```text
GET  /api/v1/health
GET  /api/v1/status
GET  /api/v1/status/full
GET  /api/v1/capabilities

POST /api/v1/slit
POST /api/v1/slit_angle

GET  /api/v1/calibration/status
POST /api/v1/calibration/mode
POST /api/v1/calibration/lamp

GET  /api/v1/detector/config
POST /api/v1/detector/config

GET  /api/v1/observation/status
POST /api/v1/observation/arm
POST /api/v1/observation/start
POST /api/v1/observation/finish
POST /api/v1/observation/stop_readout
POST /api/v1/observation/abort_discard

GET  /api/v1/presets
POST /api/v1/presets/preview
POST /api/v1/presets/apply
```

Observation router 当前覆盖 single-exposure lifecycle。Presets router 当前覆盖 catalog、preview、guarded apply。Health router 当前提供 health、status、status/full、capabilities。

### 5.3 Kernel / Runtime 基线

当前 runtime 已经具备：

```text
- RunMode: sim / real
- system/slit/lamps/detector/health 子系统状态聚合
- exposure_state 聚合
- latest_job 查询
- capabilities map
- SIM adapter 装配
- REAL adapter NotImplemented 边界
```

Job 层已经能记录 command request、job status、accepted/running/succeeded/failed/aborted、state_before/state_after、result、error 等信息。Dispatcher 层把 invalid param / invalid state / unsupported 作为 non-fault rejection 处理，而不是一概把系统打入 FAULT。

## 6. 已完成的关键工作

```text
Phase 2.6:
  GUI 与运行状态基础。
  完成 /api/v1/status/full、operational status 思路、v6 review shell、v5 adapter、UI safety switches 和 X-Request-ID / latest-job 方向。

Phase 2.7:
  Preset operational hardening。
  完成 preset category / risk_level / requires_confirmation、side-effect-free preview、guarded apply、latest-job linkage。

Phase 2.8-G:
  v7 runtime 架构稳定。
  完成 v7 runtime master gate、模块级 runtime gates、status/preset/observe/guard runtime 的 skeleton-aware 化。

Phase 2.8-H:
  v5 到 v7 feature parity pass。
  完成 v7.1 IA、Instrument / Configure 页面、feedback rail、Observe Finish baseline、Instrument API alignment、slit arcsec/um dual-unit correction。

Phase 2.8-I/J:
  command feedback unification 与 v7 default route switch。
  /ui 默认进入 v7.1 operator-console prototype，/ui/v5 和 /ui/legacy 保留 fallback。

v7 UI IA cleanup:
  ui_operational_v7.html 成为 served layout source；Instrument 页面压缩为 operator-facing compact structure；Setup 页面改为 action-oriented structure；MODS-inspired gap review 写入 operator-console requirements。
```

P0/v5 slit-width 单位合同继续保留：

```text
1 arcsec = 128.34 um
operator unit = arcsec
backend command unit = um
```

## 7. 当前能力分级

| 能力 | 当前状态 | 策略判断 |
|---|---|---|
| 分层架构 | 已成型 | 继续保持 Domain / Kernel / Application / API / UI / Adapter 边界 |
| Request ID / Job audit | 已成型 | 后续 OCS、sequence、data product 都必须沿用 |
| Setup/Data Context | UI 有占位与字段，尚无 durable backend | Phase 2.9-A 首先补齐 |
| Observation single exposure | 已可用 | 短期继续作为 Observe 的核心，不急于强行做完整 sequence runner |
| Preset preview/apply | 已可用 | 后续需要 operator-facing diff polish |
| v7 default UI | 已切换 | 是默认 prototype，不是 final GUI |
| v7 runtime | 默认关闭 | 保持显式 opt-in，避免扩大控制面 |
| Slit control | 基础可用 | arcsec/um 双单位合同必须固定 |
| Calibration | 基础可见/可控 | 后续需区分 lamp/source/path/mirror，不要简化成 lamp on/off |
| Detector config | 可见，部分可写 | routine UI 不应急着开放复杂 detector write |
| B/G/R channels | UI summary 级别可见 | 真实三通道硬件控制是后续硬件集成 |
| OCS | 未实现 | Phase 2.9 先定义合同，Phase 3.x 再接 adapter |
| TCS | 未实现 | 先做 read-only status/readiness，不做 slew/focus 控制 |
| FITS/data product | 未实现 | 先定义 ExposureRecord/DataProduct contract，再做 writer |
| Slit monitor/guider | 未实现 | 保留 visible placeholder，后续接 image feed |
| 底层硬件通信协议 | 未确定 | 由真实硬件选型决定；当前只保留 adapter/gateway 边界 |
| Auth/role gating | 未实现 | 产品化前必须补，但不应早于核心 workflow contract |

## 8. 逻辑架构

```mermaid
flowchart TB
  OCS["OCS / Future Observing Plan"]
  Operator["Operator Console v7.1"]
  TCS["TCS Context<br/>Read Only First"]

  subgraph ICS["JUST Long-Slit ICS 2.0"]
    API["API and UI Entry<br/>FastAPI /api/v1 / UI Routes / Request ID"]
    APP["Application Layer<br/>Services / Dispatcher / Use Cases"]
    DOMAIN["Domain Layer<br/>Setup / Observation / Detector / Calibration / Slit / Presets"]
    KERNEL["Kernel Layer<br/>Runtime / States / Jobs / Guards"]
    ADAPTER["Adapter Layer<br/>Slit / Calibration / Detector / Future OCS-TCS-Data"]
    DRIVER["Driver Layer<br/>Simulation Drivers Now / Real Drivers Later"]
  end

  DATA["Data Product Layer<br/>ExposureRecord / FITS / Quicklook / Audit"]
  HW["Hardware Layer<br/>Slit / Lamps / Detector B-G-R / SlitCam"]
  HWIF["Hardware Interface TBD<br/>Controller / SDK / Fieldbus if required"]

  Operator --> API
  OCS -. "Phase 3.x" .-> API
  TCS -. "status and readiness" .-> API

  API --> APP
  APP --> DOMAIN
  APP --> KERNEL
  KERNEL --> ADAPTER
  ADAPTER --> DRIVER

  DRIVER --> HW
  DRIVER -. "Phase 4.x if required" .-> HWIF

  APP --> DATA
  KERNEL --> DATA
```

关键点：OCS/TCS/Data Product/未来硬件接口都不应该绕过 Application/Kernel 直接进入 UI 或硬件。所有命令必须穿过统一的状态、审计、错误和安全边界。底层硬件通信协议保持 TBD，由真实硬件选型反向驱动。

## 9. 数据与控制流目标

```mermaid
sequenceDiagram
    participant O as Operator / OCS
    participant API as FastAPI API
    participant APP as Application Service
    participant D as Domain Models
    participant K as Kernel Runtime / Jobs
    participant A as Adapter
    participant HW as Driver / Hardware
    participant DP as Data Product Layer

    O->>API: Setup context / Observation intent / Command
    API->>APP: validate request schema
    APP->>D: validate domain contract
    APP->>K: create CommandRequest + JobRecord
    K->>K: check state / interlocks / capability
    K->>A: dispatch safe command
    A->>HW: sim or real operation
    HW-->>A: status/result
    A-->>K: normalized result/error
    K->>K: update state + latest_job
    K->>DP: record exposure/event metadata
    DP-->>APP: data product reference
    APP-->>API: response with request_id/latest_job/result
    API-->>O: operator-facing result
```

目标不是让每个按钮直接控制硬件，而是让每个操作都成为可追踪、可恢复、可解释的 command lifecycle。

## 10. 产品级目标定义

ICS 2.0 达到产品级，并不意味着“没有任何 bug”。更实际的定义是：

```text
- routine observing 可以通过 v7 operator console 完成；
- OCS 可以提交观测请求，并查询状态和结果；
- TCS 状态可以进入 readiness 判断，但早期不由 ICS 控制 TCS；
- Setup、仪器配置、曝光、定标、数据产品和错误都具备统一生命周期；
- 所有高影响操作都有 request_id、latest_job、result_summary、last_error；
- Abort / discard / preset apply / engineering action 有明确 guard；
- 真实硬件接入遵守 adapter contract，不破坏模拟链路；
- 故障可以被检测、隔离、解释，并有人工恢复路径；
- 数据产品至少包含可追溯 metadata、quicklook 入口和后续 FITS/manifest 合同；
- operator flow 和 diagnostics flow 明确分离。
```

最终成熟形态：

```text
OCS / Operator / Future Script
  -> SetupContext / ObservationRequest / ObservationPlan
  -> ICS validation and readiness
  -> SequenceStep execution
  -> Slit / calibration / detector / TCS-readiness coordination
  -> ExposureRecord / DataProduct / Quicklook
  -> Lifecycle event stream
  -> Result callback / audit log
  -> Safe abort and recovery
```

## 11. Phase 2.9：Contract Hardening

Phase 2.9 的核心不是“大规模实现”，而是把 Phase 3.x/4.x 需要的合同定稳。Phase 2.9 应从 durable Setup/Data Context 开始，因为它是后续 ObservationRequest、ExposureRecord、DataProduct、OCS adapter、FITS/manifest、audit/recovery 的上游事实源。

### 2.9-A：Setup/Data Context model + API + persistence

目标：把 Setup 从 frontend-only placeholder 推进为 durable backend fact source。

产物：

```text
SessionDataContext
SetupContextService
SetupContextStore protocol
GET /api/v1/setup/context
PUT /api/v1/setup/context
POST /api/v1/setup/context/reload, if justified after persistence lands
storage-simple JSON implementation first, unless a stronger persistence need appears
```

建议最小拆分：

| Slice | 目标 | 不做 |
|---|---|---|
| 2.9-A1 | domain model + domain tests | 不接 API，不接 persistence，不改 UI |
| 2.9-A2 | read-only API skeleton + service default | 不写磁盘，不做 save |
| 2.9-A3 | persistence port + JSON store | 不接 observation lifecycle |
| 2.9-A4 | save/reload API | 不做 proposal DB，不做 scheduler |
| 2.9-A5 | UI runtime binding | 不扩大 Setup 页面功能范围 |
| 2.9-A6 | observation metadata handoff | 不在此阶段决定复杂 frame-index 消耗策略 |

字段起点：

```text
observers
project_id
pi_name
support_operator
root_name
date_prefix
comment
next_frame_index
data_directory
```

派生字段：

```text
next_frame_token
file_stem_preview / data_preview
```

原则：持久化 `next_frame_index`，不要把 `next_frame_token` 当 source of truth。token 是显示层派生结果；index 才是以后安全递增、回滚、占号策略讨论的核心状态。

### 2.9-B：Observation request/preview contract

产物：

```text
ObservationRequest
ObservationPlan
SequenceStep
ExposureSpec
AbortPolicy
RecoveryPolicy
ObservationLifecycle
```

要求：

```text
- 可 validate；
- 可 dry-run；
- 可 preview；
- 不直接执行完整 sequence；
- 不接真实 OCS；
- 不接真实 TCS；
- 不引入硬件依赖。
```

### 2.9-C：Shared command/status feedback contract

产物：

```text
CommandFeedback
EventEnvelope
CommandResultEnvelope
LifecycleEvent
ErrorEnvelope
```

统一字段：

```text
event_id
request_id
observation_id
command_id
job_id
source
severity
timestamp
state_before
state_after
last_command
latest_job
last_error
result_summary
error_code
payload_ref
freshness
```

目标：把 v7 feedback rail 和各页面 command summary 的 vocabulary 提升到后端 read model，而不是继续散落在页面绑定中。

### 2.9-D：Data product and exposure-record contract

产物：

```text
ExposureRecord
FrameRecord
DataProductRef
QuicklookRef
FitsHeaderSummary
QualityFlag
SequenceManifest
```

目标：先把“曝光成功”和“数据产品存在”区分开。当前 observation status 中已有 `observation_meta`、`frame_results` 等雏形，但还不是完整持久化数据产品系统。

### 2.9-E：Read-only observatory/TCS context

产物：

```text
TcsStatus
ObservatoryContext
ReadinessStatus
```

早期只读字段候选：

```text
connected
stale
tracking_state
target_name
ra_dec
alt_az
rotator_angle
focus_position
focus_validity
weather_ok
dome_ready
telescope_ready
last_updated
```

明确不做：

```text
- 不 slew；
- 不 focus adjustment；
- 不 rotator command；
- 不 guiding command；
- 不 dome command；
- 不 weather authority；
- 不伪造真实 telescope telemetry。
```

### 2.9-F：Operator workflow polish

重点：

```text
- Presets preview 从 raw JSON 走向 operator-facing diff；
- Setup 明确 local placeholder / persisted contract / runtime-derived；
- Diagnostics 成为 raw payload、runtime、request、latest_job、error 的主入口；
- Instrument / Observe / Presets 的 busy / blocked / error / result visual language 统一；
- Housekeeping 与 Engineer 的 routine/unsafe 边界逐步明确。
```

## 12. Phase 3.x：Simulated End-to-End Observatory Workflow

Phase 3.x 才开始把“合同”变成“端到端模拟观测系统”。

### Phase 3.0：Sequence Runner MVP

```text
- ObservationPlan -> SequenceStep list；
- dry-run -> execute；
- step result history；
- pause / abort / fail / recover；
- simulator-backed only；
- UI Observe 增加 sequence monitor，但保留 single-exposure baseline。
```

### Phase 3.1：OCS Adapter MVP

候选接口：

```text
POST /api/v1/ocs/observations
GET  /api/v1/ocs/observations/{observation_id}
POST /api/v1/ocs/observations/{observation_id}/abort
GET  /api/v1/ocs/events
```

关键原则：

```text
- OCS adapter 接收观测意图；
- ICS 负责 validation/readiness/sequence execution/status/result；
- OCS 不直接控制硬件；
- idempotency key 和 request_id 必须进入审计链。
```

### Phase 3.2：TCS read-only sync

```text
- TCS simulator adapter；
- recorded JSON replay adapter；
- real read-only adapter；
- readiness rules；
- v7 status visibility。
```

只读优先，不做望远镜控制。

### Phase 3.3：Data product / quicklook backend

```text
- ExposureRecord；
- file watcher；
- quicklook placeholder/latest image；
- FITS header summary；
- B/G/R frame mapping；
- data product status；
- quality flags。
```

FITS writer 可以在这一阶段开始，但应服务于真实数据产品合同，不要先写孤立的 FITS demo。

### Phase 3.4：Realtime event push, if still justified

```text
- SSE or WebSocket, after EventEnvelope is stable；
- lifecycle events；
- command result events；
- observation step updates；
- status freshness；
- polling fallback。
```

实时推送不宜早于 EventEnvelope 和 sequence lifecycle 稳定；如果 polling + command feedback 足够支持当前阶段，则继续保留为后续候选。

### Phase 3.5：v7 production-candidate hardening

```text
- v7 不只是 default prototype，而是 production candidate；
- role boundary 初步进入；
- operator/diagnostics/engineer 信息分区完成；
- local deployment checklist；
- route fallback strategy 保留。
```

## 13. Phase 4.x：Hardware Commissioning

Phase 4.x 是真实硬件接入和现场 commissioning，不是简单地把 simulator 替换为 hardware。

### Phase 4.0：Hardware adapter contract freeze

```text
SlitAdapter
CalibrationAdapter
DetectorAdapter
SlitMonitorAdapter
TcsAdapter
SafetyInterlockAdapter
PowerAdapter, if required
HardwareGatewayAdapter, if required
VendorSdkAdapter, if required
FieldbusAdapter, if required
```

每个 adapter 必须有：

```text
sim implementation
real implementation placeholder
capabilities
health/status
command API
abort/stop behavior
timeout policy
error mapping
recovery behavior
tests
```

### Phase 4.1：Slit / calibration bring-up

```text
- Engineer-only first；
- hardware-in-loop tests；
- interlock；
- timeout；
- position verification；
- command/result audit；
- manual recovery。
```

### Phase 4.2：Detector B/G/R bring-up

```text
- read-only status；
- config read-only；
- test exposure；
- dark/bias；
- science exposure；
- readout；
- data product registration；
- quicklook。
```

### Phase 4.3：Slit monitor / guider integration

```text
- latest frame；
- slit region visualization；
- target-on-slit；
- slit-width measurement；
- guide offset suggestion；
- operator-confirmed correction。
```

自动闭环应放到很后面，不能早期直接启用。

### Phase 4.4：Hardware communication and realtime feedback integration, if required

真实硬件通信协议不在软件阶段预先指定。Phase 4.x 根据最终硬件、控制器、厂商 SDK、PLC/fieldbus 架构和现场 commissioning 需求决定接入方式。若硬件确实使用某种 fieldbus、motion controller、PLC、EPICS IOC、串口、USB、以太网或厂商 SDK，ICS 只通过 adapter/gateway 进入，不让 routine operator UI 直接面对底层接口。

```text
Engineer-only first
sim parity required
safe stop verified, if applicable
watchdog verified, if applicable
hardware map documented
fault mapping stable
no browser-to-hardware direct control
```

### Phase 4.5：Nightly commissioning

```text
- daytime checkout；
- night startup；
- calibration sequence；
- science sequence；
- abort/recovery drill；
- data product verification；
- operator checklist；
- incident log。
```

## 14. 工作优先级

### P0：现在到 Phase 2.9-A 必须推进

```text
1. 以 Setup/Data Context 作为 Phase 2.9-A 的第一入口；
2. 建立 SessionDataContext domain model；
3. 建立最小 API/application service/persistence 合同；
4. 保持 Setup 不膨胀成 proposal database 或 scheduler；
5. 保持 B/G/R 为 honest summary，不启动 per-channel exposure readiness/control；
6. 保持 telescope/OCS/TCS 为 read-only context 或 future feedback candidate，不做直接望远镜控制；
7. 保持 pytest -q 绿色。
```

### P1：Phase 2.9-B 到 2.9-F

```text
1. Observation request/preview contract；
2. Shared command/status feedback contract；
3. ExposureRecord/DataProduct contract；
4. Read-only observatory/TCS context；
5. Presets diff 与 Diagnostics/Housekeeping/Engineer 边界 polish。
```

### P2：Phase 3.x

```text
1. Sequence Runner MVP；
2. OCS Adapter MVP；
3. TCS read-only sync；
4. Data product / quicklook backend；
5. Event push if justified。
```

### P3：Phase 4.x

```text
1. real slit/calibration hardware；
2. detector B/G/R bring-up；
3. slit monitor / guider；
4. hardware communication protocol validation；
5. commissioning checklists and drills。
```

## 15. 硬件现实约束

后续所有软件设计必须遵守以下原则：

```text
软件只表达、验证、记录和协调仪器能力；
软件不能伪造硬件能力；
软件不能替代光学设计；
软件不能越过 adapter/safety/kernel 直接控制硬件；
软件不能让 operator UI 暴露未验证的低层工程控制；
软件必须把 unavailable / stale / simulated / real 清楚显示。
```

具体到当前 P0 约束：

```text
- B/G/R 三通道必须始终按 JUST 模型表达，不能退化为 Blue/Red 两通道；
- slit width 控制必须保留 arcsec 和 um 双单位；
- 1 arcsec = 128.34 um 是软件控制合同；
- calibration 不只是 lamp on/off，还包括 source、mode、path、mirror 等后续合同；
- slit monitor / guider 是一等子系统，不应从 UI 架构中消失；
- TCS context 是 readiness 的组成部分，但早期只读；
- 底层通信协议由硬件选型决定；当前阶段不预设任何具体 fieldbus 或厂商接口。
```

## 16. Phase 2.9-A 第一小步

Phase 2.9-A1 只做 domain model 与 domain tests。

```text
目标：
  冻结 SessionDataContext 领域模型。

不做：
  不加 router。
  不加 service。
  不加 JSON persistence。
  不改 ui_operational_v7.html。
  不改 runtime_status.js。
  不把 next_frame_index 消耗语义接进 exposure lifecycle。

交付：
  src/justls/ics/domain/setup/context.py
  src/justls/ics/domain/setup/__init__.py
  tests/domain/test_setup_context.py

验收：
  pytest tests/domain/test_setup_context.py
  pytest -q
```

## 17. 成功标准

短期成功：

```text
- README / docs / main.py route 描述一致；
- pytest -q 持续绿色；
- Phase 2.9-A 从 Setup/Data Context 后端事实源开始；
- 每个小步提交有清晰边界；
- v7 作为默认入口不扩大 runtime 控制面；
- 新技术名词进入路线图前通过 Technology Adoption Gate。
```

中期成功：

```text
- SetupContext 能被 ObservationRequest / ExposureRecord / DataProduct 复用；
- command/status feedback 不再散落在 UI 内部；
- OCS/TCS/Data Product 合同清楚，但不越权、不伪造硬件能力；
- simulator-backed end-to-end observing workflow 可跑通。
```

长期成功：

```text
- routine observing 可以通过 operator console 完成；
- OCS 可以提交观测意图并查询状态/结果；
- 真实硬件通过 adapter contract 接入且保持 sim parity；
- 故障、abort、discard、engineering recovery 都可追踪、可解释、可人工恢复。
```
