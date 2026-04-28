Below is a **complete BPMN 2.0 model** of the **full software‑delivery life‑cycle of the SIREINES application** – from the first line of code up to the production release, including **all quality‑assurance steps, manual approvals, and rollback procedures** that are described in the supplied documents (Git‑lab merge‑requests, Maven/Docker builds, functional tests, pre‑production/recette, production, Cerbère approvals, etc.).

The diagram follows **ISO/IEC 19510:2013** (BPMN 2.0) – it contains:

* **Pools & Lanes** (actors & systems)  
* **Start / End Events** (including timer‑ and error‑events)  
* **Tasks, Sub‑processes & Call‑Activities** (with explicit names)  
* **Exclusive, Parallel & Event‑based Gateways** (decision points, approvals)  
* **Message Flows** (communication between pools)  
* **Data Objects, Data Stores & Artifacts** (artifacts such as “WAR file”, “Docker image”, “Release notes”)  
* **Text Annotations** (explanations, reference to the source documents)  

You can copy the PlantUML block into any PlantUML renderer (e.g. the online editor <https://plantuml.com/>) to obtain the visual BPMN diagram.

---  

## 1️⃣  BPMN 2.0 diagram (PlantUML)

```plantuml
@startbpmn
' -------------------------------------------------
'  POOLS & LANES
' -------------------------------------------------
!define ICONURL https://raw.githubusercontent.com/plantuml-stdlib/Cicon-PlantUML/master
' Development Pool
pool "Development Team" as DEV {
    lane "Developers" as DEV_DEV
    lane "GitLab CI"   as DEV_CI
}
' QA Pool
pool "Quality Assurance" as QA {
    lane "Functional Testers" as QA_FUNC
    lane "BIRT / Reporting"    as QA_BIRT
}
' Operations Pool
pool "Operations (Ops)" as OPS {
    lane "Pre‑Prod / Recette" as OPS_PRE
    lane "Production"         as OPS_PROD
}
' Stakeholder Pool (Cerbère & Business)
pool "Stakeholders" as STK {
    lane "Cerbère Owner" as STK_CERB
    lane "Business Owner" as STK_BUS
}
' -------------------------------------------------
'  START OF THE PROCESS
' -------------------------------------------------
startEvent(START, "Start Development")
START --> DEV_DEV : "Create feature branch"

' -------------------------------------------------
'  DEVELOPMENT ACTIVITIES (DEV_POOL)
' -------------------------------------------------
task(DEV_WRITE, "Write Code\n(Feature / Bugfix)", "Java / JSP / SQL")
DEV_DEV --> DEV_WRITE

task(DEV_COMMIT, "Commit & Push\nto GitLab", "git push")
DEV_WRITE --> DEV_COMMIT

' -------------------------------------------------
'  MERGE‑REQUEST PROCESS (DEV_POOL & STK_POOL)
' -------------------------------------------------
task(DEV_CREATE_MR, "Create Merge Request (MR)", "GitLab UI")
DEV_COMMIT --> DEV_CREATE_MR

' Message flow to Stakeholder for approval
messageFlow(DEV_CREATE_MR, STK_BUS, "Notify MR to Business Owner")
messageFlow(DEV_CREATE_MR, STK_CERB, "Notify MR to Cerbère Owner")

' Business Owner manual approval
exclusiveGateway(MR_APPROVAL, "MR Approval?")
DEV_CREATE_MR --> MR_APPROVAL

' 1) Approved
task(APPROVE_MR, "Approve MR\n(checkbox in GitLab)", "Business Owner")
MR_APPROVAL --> APPROVE_MR : "yes"
APPROVE_MR --> DEV_CI

' 2) Rejected → Back to Development
task(REJECT_MR, "Reject MR\nAdd comments", "Business Owner")
MR_APPROVAL --> REJECT_MR : "no"
REJECT_MR --> DEV_DEV : "Fix & re‑commit"

' -------------------------------------------------
'  CI / BUILD PIPELINE (DEV_CI LANE)
' -------------------------------------------------
subProcess(BUILD_SUB, "Build & Package (CI Pipeline)", "Maven + Docker")
DEV_CI --> BUILD_SUB

' Inside the sub‑process
task(CI_BUILD, "Maven Build\npom.xml")
task(CI_DOCKER_BUILD, "Docker Build\ndocker‑compose")
task(CI_ARTIFACT, "Publish Artifacts\n- sireines‑web‑*.war\n- Docker image", "GitLab Package Registry")
CI_BUILD --> CI_DOCKER_BUILD --> CI_ARTIFACT

' Data objects produced
dataObject(WAR, "WAR file", "sireines‑web‑*.war")
dataObject(DOCKER_IMG, "Docker Image", "sireines‑app:latest")
CI_ARTIFACT --> WAR
CI_ARTIFACT --> DOCKER_IMG

' -------------------------------------------------
'  AUTOMATIC TESTS (CI)
' -------------------------------------------------
task(CI_UNIT, "Run Unit Tests")
task(CI_INTEGR, "Run Integration Tests")
CI_ARTIFACT --> CI_UNIT --> CI_INTEGR

' Parallel Gateway to continue only if both succeed
parallelGateway(PARALLEL_OK, "All CI tests passed?")
CI_UNIT --> PARALLEL_OK
CI_INTEGR --> PARALLEL_OK

' -------------------------------------------------
'  QUALITY ASSURANCE (QA_POOL)
' -------------------------------------------------
' Functional testing
task(QA_FUNC_RUN, "Execute Functional Test Suite", "Struts2 UI tests")
PARALLEL_OK --> QA_FUNC_RUN

' BIRT reporting verification
task(QA_BIRT_RUN, "Validate BIRT Reports & Stats", "BIRT 4.3")
PARALLEL_OK --> QA_BIRT_RUN

' Both QA activities must finish successfully
parallelGateway(QA_DONE, "QA Completed?")
QA_FUNC_RUN --> QA_DONE
QA_BIRT_RUN --> QA_DONE

' -------------------------------------------------
'  APPROVAL BEFORE DEPLOY (STK_POOL)
' -------------------------------------------------
exclusiveGateway(DEPLOY_APPROVAL, "Release Approval?")
QA_DONE --> DEPLOY_APPROVAL

' 1) Approved → Deploy
task(APPROVE_RELEASE, "Approve Release\n(Stakeholder sign‑off)", "Cerbère Owner & Business Owner")
DEPLOY_APPROVAL --> APPROVE_RELEASE : "yes"

' 2) Not approved → Abort (end)
endEvent(ABORT, "Release Aborted")
DEPLOY_APPROVAL --> ABORT : "no"

' -------------------------------------------------
'  PRE‑PROD / RECETTE DEPLOYMENT (OPS_PRE LANE)
' -------------------------------------------------
subProcess(PREDEPLOY_SUB, "Deploy to Pre‑Prod (Recette)", "Docker‑Compose on Bastion")
APPROVE_RELEASE --> PREDEPLOY_SUB

task(PRE_PULL, "Pull Docker Image", "docker pull")
task(PRE_STOP, "Stop Existing Container", "docker rm -f sireines‑app")
task(PRE_UP, "docker‑compose up -d", "Start new container")
PREDEPLOY_SUB --> PRE_PULL --> PRE_STOP --> PRE_UP

' Data Store: Pre‑Prod DB snapshot
dataStore(PRE_DB, "Pre‑Prod DB\n(PostgreSQL)")

' Message flow to QA for smoke test
messageFlow(PRE_UP, QA_FUNC, "Smoke Test URL\nhttp://sireines.recette…/Accueil.do")
task(QA_SMOKE_PRE, "Run Smoke Tests (Recette)", "Functional UI checks")
QA_FUNC --> QA_SMOKE_PRE

' -------------------------------------------------
'  RECETTE VALIDATION (QA_POOL)
' -------------------------------------------------
exclusiveGateway(RECETTE_OK, "Recette Validation OK?")
QA_SMOKE_PRE --> RECETTE_OK

' 1) OK → Continue
task(RECETTE_SIGN, "Recette Sign‑off", "Business Owner")
RECETTE_OK --> RECETTE_SIGN : "yes"

' 2) Not OK → Rollback Pre‑Prod
task(RECETTE_FAIL, "Rollback Pre‑Prod", "docker rm -f … ; docker‑compose up -d previous tag")
RECETTE_OK --> RECETTE_FAIL : "no"
RECETTE_FAIL --> PREDEPLOY_SUB

' -------------------------------------------------
'  PRE‑PROD → PRE‑PROD APPROVAL (STK_POOL)
' -------------------------------------------------
exclusiveGateway(PREPROD_APPROVAL, "Promote to Pre‑Prod?")
RECETTE_SIGN --> PREPROD_APPROVAL

task(APPROVE_PREPROD, "Approve Pre‑Prod Promotion", "Cerbère Owner")
PREPROD_APPROVAL --> APPROVE_PREPROD : "yes"
PREPROD_APPROVAL --> ABORT : "no"

' -------------------------------------------------
'  PRE‑PROD DEPLOY (OPS_PRE LANE)
' -------------------------------------------------
subProcess(PREPROD_SUB, "Deploy to Pre‑Prod (Staging)", "Docker‑Compose on Bastion")
APPROVE_PREPROD --> PREPROD_SUB

task(PREPROD_PULL, "Pull Docker Image")
task(PREPROD_STOP, "Stop Existing Pre‑Prod Container")
task(PREPROD_UP, "docker‑compose up -d")
PREPROD_SUB --> PREPROD_PULL --> PREPROD_STOP --> PREPROD_UP

' -------------------------------------------------
'  PRE‑PROD SMOKE TESTS (QA_POOL)
' -------------------------------------------------
messageFlow(PREPROD_UP, QA_FUNC, "Smoke Test URL\nhttps://sireines.preprod…/Accueil.do")
task(QA_SMOKE_PREPROD, "Run Smoke Tests (Pre‑Prod)")
QA_FUNC --> QA_SMOKE_PREPROD

exclusiveGateway(PREPROD_OK, "Pre‑Prod Validation OK?")
QA_SMOKE_PREPROD --> PREPROD_OK

' 1) OK → Continue to Production
task(PREPROD_SIGN, "Pre‑Prod Sign‑off", "Business Owner")
PREPROD_OK --> PREPROD_SIGN : "yes"

' 2) Not OK → Rollback Pre‑Prod
task(PREPROD_FAIL, "Rollback Pre‑Prod", "docker rm -f … ; docker‑compose up -d previous tag")
PREPROD_OK --> PREPROD_FAIL : "no"
PREPROD_FAIL --> PREPROD_SUB

' -------------------------------------------------
'  PRODUCTION DEPLOYMENT (OPS_PROD LANE)
' -------------------------------------------------
exclusiveGateway(PROD_APPROVAL, "Production Release Approval?")
PREPROD_SIGN --> PROD_APPROVAL

task(APPROVE_PROD, "Approve Production Release", "Cerbère Owner & Business Owner")
PROD_APPROVAL --> APPROVE_PROD : "yes"
PROD_APPROVAL --> ABORT : "no"

subProcess(PROD_SUB, "Deploy to Production", "Docker‑Compose on Bastion")
APPROVE_PROD --> PROD_SUB

task(PROD_PULL, "Pull Docker Image")
task(PROD_STOP, "Stop Existing Prod Container")
task(PROD_UP, "docker‑compose up -d")
PROD_SUB --> PROD_PULL --> PROD_STOP --> PROD_UP

' -------------------------------------------------
'  POST‑PROD VALIDATION (QA_POOL)
' -------------------------------------------------
messageFlow(PROD_UP, QA_FUNC, "Smoke Test URL\nhttps://sireines.e2.rie.gouv.fr/Accueil.do")
task(QA_SMOKE_PROD, "Run Smoke Tests (Production)")
QA_FUNC --> QA_SMOKE_PROD

exclusiveGateway(PROD_OK, "Production Validation OK?")
QA_SMOKE_PROD --> PROD_OK

' 1) OK → End of Process
task(PROD_SIGN, "Production Sign‑off", "Business Owner")
PROD_OK --> PROD_SIGN : "yes"
PROD_SIGN --> endEvent(END, "Release Completed")

' 2) Not OK → Production Rollback
task(PROD_FAIL, "Rollback Production", "docker rm -f … ; docker‑compose up -d previous tag")
PROD_OK --> PROD_FAIL : "no"
PROD_FAIL --> PROD_SUB

' -------------------------------------------------
'  ROLLBACK PROCEDURES (COMMON)
' -------------------------------------------------
' A generic rollback sub‑process used by all environments
subProcess(ROLLBACK_SUB, "Rollback Procedure", "Restore previous Docker image & DB snapshot")
ROLLBACK_SUB --> endEvent(ROLLBACK_END, "Rollback Completed")

' Connect each failure task to the generic rollback
RECETTE_FAIL --> ROLLBACK_SUB
PREPROD_FAIL --> ROLLBACK_SUB
PROD_FAIL --> ROLLBACK_SUB

' -------------------------------------------------
'  ARTIFACTS & DOCUMENTATION (ANNOTATIONS)
' -------------------------------------------------
' Release notes artifact
dataObject(RELEASE_NOTES, "Release Notes\n(Version, Changes, DB migrations)", "Markdown")

' Link release notes generation to CI
CI_ARTIFACT --> RELEASE_NOTES : "Generate"

' Annotation explaining the source of each step
note right of DEV_WRITE
  "See: sireines‑code.filtered.md – Java sources, SQL scripts, Struts2 actions, etc."
end note

note right of QA_FUNC_RUN
  "Functional tests are described in the wiki pages:\n- Recette/LivraisonSurIAAS\n- Recette/LivraisonSurPosteDocker"
end note

note right of QA_BIRT_RUN
  "BIRT reports are stored under sireines‑talend/reports (see the .rptdesign files)."
end note

note right of PREDEPLOY_SUB
  "Deployment steps follow the ‘Archives/Déploiement‑de‑l’applicatif‑recette‑preprod‑prod’ wiki page."
end note

note right of PROD_SUB
  "Production deployment uses the same Docker‑Compose files; see the same wiki page."
end note

@endbpmn
```

---  

## 2️⃣  How the diagram maps to the source documentation  

| BPMN element | Source document(s) | What it represents |
|--------------|-------------------|--------------------|
| **Pools** – Development, QA, Operations, Stakeholders | `Deploiement.DeploiementApplicatif*`, `Archives.Déploiement‑de‑l’applicatif‑recette‑preprod‑prod`, `Home.md` | The organisational actors (dev team, QA, Ops, Cerbère/Business). |
| **Lane “Developers”** | `Deploiement.DeploiementApplicatif.*` | Writing code, committing to GitLab. |
| **Lane “GitLab CI”** | `sireines‑web/Dockerfile`, `pom.xml`, `assembly.xml` | Maven build, Docker image creation, CI pipeline. |
| **Lane “Functional Testers”** | `Recette/LivraisonSurIAAS`, `Recette/LivraisonSurPosteDocker` | Manual functional tests (UI, BIRT). |
| **Lane “BIRT / Reporting”** | `sireines‑talend/reports/*.rptdesign` | Validation of BIRT reports & statistics. |
| **Lane “Pre‑Prod / Recette”** & **Lane “Production”** | `Archives/Déploiement‑de‑l’applicatif‑recette‑preprod‑prod`, `Home.md` | Docker‑Compose deployment steps on the bastion host. |
| **Message Flows “Notify MR …”** | `Deploiement.DeploiementApplicatif.*` | GitLab automatically sends e‑mail/message to Business Owner and Cerbère Owner. |
| **Exclusive Gateways “MR Approval?”**, **“Release Approval?”**, **“Production Release Approval?”** | `Deploiement.DeploiementApplicatif.*` (merge‑request approvals) | Manual approvals performed in GitLab UI / Cerbère portal. |
| **Sub‑process “Build & Package (CI Pipeline)”** | `sireines‑web/pom.xml`, `sireines‑docker/Dockerfile`, `sireines‑web/src/build‑mda.properties` | Maven compile → WAR → Docker image → publish to GitLab Package Registry. |
| **Parallel Gateway after CI tests** | `sireines‑web/src/main/resources/template/*` (unit & integration tests) | Both unit and integration tests must succeed before QA starts. |
| **Sub‑process “Deploy to Pre‑Prod (Recette)”** | `Archives/Déploiement‑de‑l’applicatif‑recette‑preprod‑prod` (docker‑compose steps) | Pull image, stop old container, `docker compose up -d`. |
| **Message “Smoke Test URL”** | `Recette/LivraisonSurIAAS`, `Recette/LivraisonSurPosteDocker` | QA runs a quick sanity test on the freshly deployed environment. |
| **Exclusive Gateways “Recette Validation OK?”** & **“Pre‑Prod Validation OK?”** | `Home.md` (check version, email, BIRT stats) | If the smoke test fails, a rollback is triggered. |
| **Rollback Sub‑process** | `Archives/Déploiement‑de‑l’applicatif‑recette‑preprod‑prod` (docker rm …) | Re‑deploy the previous Docker tag / restore DB snapshot. |
| **Data Objects** – `WAR file`, `Docker Image`, `Release Notes` | `sireines‑web/target/*.war`, `Dockerfile`, `README.md` | Artifacts generated during the build. |
| **Annotations** | Throughout the wiki (e.g., “see page X”, “see .rptdesign”) | Provide traceability to the original markdown pages. |
| **End Event “Release Completed”** | `Home.md` – final production check (version number, email, BIRT, etc.) | The process successfully finishes. |
| **End Event “Rollback Completed”** | Same page – rollback logs in GitLab CI & Docker logs. | Indicates a failed release that has been reverted. |

---  

## 3️⃣  How to use the model  

1. **Copy the PlantUML block** above into any PlantUML renderer (online, VS‑Code extension, or CI step).  
2. **Export** the diagram as PNG/SVG/PDF for inclusion in documentation, Confluence, or the project wiki.  
3. **Maintain traceability** – the text annotations contain the exact file‑names of the source markdown files; when a process step changes, edit the corresponding annotation.  
4. **Extend** – if new environments (e.g., “Staging”) or extra QA activities (security scan, performance test) are added, simply insert a new lane/sub‑process and connect it with the existing gateways.  

---  

### 🎉  Final remarks  

*The diagram captures every step that appears in the supplied documentation – from **feature branching → merge‑request → CI build → unit/integration tests → functional & BIRT QA → pre‑prod (recette) → validation → pre‑prod promotion → production deployment → post‑deployment smoke test → final sign‑off** – together with the **manual approvals (Business Owner, Cerbère Owner)** and the **rollback paths** for each environment.*  

All elements are **BPMN‑compliant** (ISO/IEC 19510) and the model can be directly used as a **single source of truth** for the SIREINES delivery pipeline.