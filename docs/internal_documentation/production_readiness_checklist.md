# ROAK SDK Production Readiness Checklist

This checklist helps move the SDK from **developer-friendly** to **production-ready**.

Use it in two phases:
- **Phase 1 (Internal rollout):** colleagues inside your organization start using it.
- **Phase 2 (External rollout):** outside clients use it and depend on stable behavior.

For each item, you get:
- **What to do** (action)
- **Plain-language explanation** (for semi-technical readers)
- **Why this is important** (business and reliability impact)

---

## Phase 1 — Internal Rollout (Colleagues)

### 1) Add automated tests for critical paths
- **What to do:** Add unit tests for authentication, token refresh, request logic, feed resolution, and semantic object behavior. Add small integration tests against a safe test environment.
- **Plain-language explanation:** Tests are automatic checks that confirm the SDK still works after changes.
- **Why this is important:** Without tests, small code changes can silently break workflows for your colleagues.

### 2) Add CI checks on every pull request
- **What to do:** Create CI workflows to run formatting/linting, type checks, tests, package build, and security scans on each PR.
- **Plain-language explanation:** CI is an automated quality gate that runs in the cloud before code is merged.
- **Why this is important:** It prevents broken or risky code from entering main branches and improves team confidence.

### 3) Harden network reliability in HTTP client
- **What to do:** Add default request timeout, retries with backoff for transient failures (e.g., 429/5xx), and shared HTTP session/connection pooling.
- **Plain-language explanation:** Network calls fail sometimes; the SDK should recover from short outages automatically.
- **Why this is important:** Users experience fewer random failures and support teams get fewer incident tickets.

### 4) Standardize public error messages and exception types
- **What to do:** Replace mixed generic exceptions with SDK-specific exceptions and consistent error messages.
- **Plain-language explanation:** Errors should be predictable and understandable for users.
- **Why this is important:** Better errors reduce debugging time and make integrations easier to maintain.

### 5) Define supported versions and pin dependencies
- **What to do:** Publish supported Python versions and API compatibility policy. Pin runtime/dev dependencies to safe ranges.
- **Plain-language explanation:** Everyone should know which software versions are guaranteed to work.
- **Why this is important:** Prevents “works on my machine” problems and reduces breakage after dependency updates.

### 6) Convert scenarios into repeatable tests
- **What to do:** Keep scenarios as examples, but migrate critical scenario validations into automated tests.
- **Plain-language explanation:** Demo scripts are useful to learn, but they are not a reliable quality gate.
- **Why this is important:** Real tests can run automatically and catch regressions early.

### 7) Add clear developer and support documentation
- **What to do:** Expand docs with setup, auth troubleshooting, common errors, and expected response patterns.
- **Plain-language explanation:** People should be able to solve common issues without asking a core developer.
- **Why this is important:** Faster onboarding and less time spent in support chats.

### 8) Add release discipline and ownership
- **What to do:** Define code owners, PR review rules, release checklist, and rollback steps.
- **Plain-language explanation:** Clear process avoids confusion when things go wrong.
- **Why this is important:** Better operational control, fewer deployment mistakes, faster recovery.

---

## Phase 2 — External Client Rollout

### 9) Define and enforce API stability policy
- **What to do:** Use semantic versioning, maintain changelog, and define deprecation windows for breaking changes.
- **Plain-language explanation:** External clients need predictable upgrades and enough notice for changes.
- **Why this is important:** Reduces client frustration and protects trust in your SDK.

### 10) Add backward-compatibility checks
- **What to do:** Add tests that verify old usage patterns still work for non-breaking releases.
- **Plain-language explanation:** New versions should not unexpectedly break existing client code.
- **Why this is important:** Prevents outages for paying clients and reduces urgent hotfixes.

### 11) Strengthen security baseline
- **What to do:** Run dependency vulnerability scans, secret scanning, static analysis, and regular credential rotation checks.
- **Plain-language explanation:** Security checks look for weak points before attackers do.
- **Why this is important:** Protects customer data, reduces legal/compliance risk, and avoids reputational damage.

### 12) Improve observability and diagnostics
- **What to do:** Add structured logs, request correlation IDs, and optional debug context that is safe to share.
- **Plain-language explanation:** When something breaks, logs should quickly show what happened.
- **Why this is important:** Faster incident resolution and lower support costs.

### 13) Validate scale behavior (pagination/rate limits/performance)
- **What to do:** Test high-volume asset queries, pagination behavior, and rate-limit handling.
- **Plain-language explanation:** What works for small datasets can fail for large real-world client accounts.
- **Why this is important:** Ensures the SDK remains reliable for both small and large customers.

### 14) Build a secure and reproducible release pipeline
- **What to do:** Automate package build/publish (TestPyPI → PyPI), verify install on clean environments, and sign release artifacts.
- **Plain-language explanation:** Every release should be built the same way and be easy to verify.
- **Why this is important:** Reduces release risk and increases customer confidence in package integrity.

### 15) Define client support model and SLAs
- **What to do:** Publish support channels, response targets, issue templates, and severity definitions.
- **Plain-language explanation:** Clients need to know how and when they can get help.
- **Why this is important:** Sets expectations, improves satisfaction, and helps your team prioritize incidents.

---

## Practical Exit Criteria

Use these criteria before each phase launch.

### Exit criteria for Phase 1 (internal)
- Critical automated tests exist and pass reliably.
- CI blocks merge on lint/type/test/build/security failures.
- Error model is consistent and documented.
- Auth and token refresh behavior is tested.
- Team has a release + rollback checklist.

### Exit criteria for Phase 2 (external)
- Versioning/changelog/deprecation policy is active.
- Backward-compatibility checks pass for supported flows.
- Security scanning is scheduled and monitored.
- Load/rate-limit/pagination behavior is validated.
- Support process and ownership are published.

---

## Suggested Ownership (example)

- **SDK Maintainers:** tests, architecture, API stability
- **DevOps/Platform:** CI/CD, release automation, artifact signing
- **Security/Compliance:** scanning, secret hygiene, policy checks
- **Developer Relations / Support:** docs, onboarding, support process

---

## Suggested Timeline (example)

- **Week 1–2:** tests + CI + network hardening + error consistency
- **Week 3:** release process + docs + internal onboarding
- **Week 4:** internal pilot with colleagues, collect feedback
- **Week 5–6:** compatibility/security/performance hardening
- **Week 7:** external beta
- **Week 8:** external GA (general availability)
