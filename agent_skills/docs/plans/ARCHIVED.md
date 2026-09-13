# Archived plans

Done plan directories removed from `docs/plans/` via git rm. Each entry's command shows that plan's delete commit.

## 2026-08-15-94xad9m8-nuclear-blind-review-done

**Title:** Nuclear blind review

**Commit:** `3a486df9b87d8e3f0f769f4061523621b3a231ee`

Renamed thermo-nuclear to nuclear-review and split its standards into a code bar and a plan bar. Added nuclear-blind-review: a slash-only isolation skill that reviews through a stripped tree and a fresh subagent. Open the diff for the isolation protocol, bar split, and blind-review CLI contracts the living skills still follow.

```bash
git show 3a486df9b87d8e3f0f769f4061523621b3a231ee
```

## 2026-08-16-6dd9208t-lossless-skill-densify-done

**Title:** Lossless densify of plan-skill prompts

**Commit:** `0ddffd04020540bc7527bcd809614b716dce032d`

Cut tokens from create-multi-stage-plan and implement-pending-plans without changing mint, picker, archive, or status behavior. Open the diff to see which sentences were restatement versus load-bearing.

```bash
git show 0ddffd04020540bc7527bcd809614b716dce032d
```

## 2026-08-16-hh7vjr2b-collision-free-plan-ids-done

**Title:** Collision-free plan directory ids

**Commit:** `3d48fb58a5389c304b1bd7b53ff393e8dc370fa0`

Replaced the shared incrementing plan-directory counter with a minted date-id-slug basename and a picker that matches path, basename, or field. Open the diff for the mint uniqueness rule and the implement selection sentence the skills still point at.

```bash
git show 3d48fb58a5389c304b1bd7b53ff393e8dc370fa0
```

## 2026-08-20-2fpurujv-archive-done-multi-select-done

**Title:** Multi-select for archive-done-plans

**Commit:** `cffb23e25af2a020fd9329b103d450bcc545c623`

Changed archive-done-plans so a picker ask is multi-select with Archive all first, then archives the selected set in basename order. Open the diff for the Archive-all-wins rule and the stop-the-batch-on-index-failure contract.

```bash
git show cffb23e25af2a020fd9329b103d450bcc545c623
```

## 2026-08-20-6z75bga5-archive-done-plans-done

**Title:** Archive done plans

**Commit:** `9b87703b3c2e352debf394a504c0be2c2b019d7b`

Added the archive-done-plans skill: git-rm a finished *-done plan directory and index it in ARCHIVED.md so agents can recover the tree with git show. Open the diff for the two-commit SHA rule and the index entry format.

```bash
git show 9b87703b3c2e352debf394a504c0be2c2b019d7b
```

## 2026-08-21-9iuxnqqu-construction-contracts-done

**Title:** Construction contracts

**Commit:** `rm 'agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/01-write-time-contract.md'
rm 'agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/02-review-time-lint.md'
rm 'agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/03-implement-files-contract.md'
rm 'agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/context/design.md'
[main 45def2e] docs(agent_skills): archive construction-contracts
 4 files changed, 196 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/01-write-time-contract.md
 delete mode 100644 agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/02-review-time-lint.md
 delete mode 100644 agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/03-implement-files-contract.md
 delete mode 100644 agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/context/design.md
45def2ebf6af9d61190622b30d2ba71f58006c1b`

Made Files a closed path contract in create-multi-stage-plan, so write-time refuses a Steps/Files mismatch, plan-bar fails a broken list, and implement cannot invent a path outside this stage's Files. Open the diff for the prefix-vs-exact rule and the implement append-or-block sentence the three skills still follow.

```bash
git show rm 'agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/01-write-time-contract.md'
rm 'agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/02-review-time-lint.md'
rm 'agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/03-implement-files-contract.md'
rm 'agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/context/design.md'
[main 45def2e] docs(agent_skills): archive construction-contracts
 4 files changed, 196 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/01-write-time-contract.md
 delete mode 100644 agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/02-review-time-lint.md
 delete mode 100644 agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/03-implement-files-contract.md
 delete mode 100644 agent_skills/docs/plans/2026-08-21-9iuxnqqu-construction-contracts-done/context/design.md
45def2ebf6af9d61190622b30d2ba71f58006c1b
```

## 2026-08-22-xknvle9g-notify-skill-done

**Title:** Notify skill

**Commit:** `rm 'agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/01-notify-cli.md'
rm 'agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/02-notify-skill.md'
rm 'agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/03-notify-me-alias.md'
rm 'agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/context/design.md'
[main 5e5d952] docs(agent_skills): archive notify-skill
 4 files changed, 232 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/01-notify-cli.md
 delete mode 100644 agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/02-notify-skill.md
 delete mode 100644 agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/03-notify-me-alias.md
 delete mode 100644 agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/context/design.md
5e5d952a149eb813d0dac8e7d9401014fe4bc6a5`

Added notify (auto-invoke) and notify-me (slash alias) plus a uv CLI that posts a desktop banner on macOS and Linux. Open the diff for the cue/yield rules, backend order, and exit codes the living skills still document.

```bash
git show rm 'agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/01-notify-cli.md'
rm 'agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/02-notify-skill.md'
rm 'agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/03-notify-me-alias.md'
rm 'agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/context/design.md'
[main 5e5d952] docs(agent_skills): archive notify-skill
 4 files changed, 232 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/01-notify-cli.md
 delete mode 100644 agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/02-notify-skill.md
 delete mode 100644 agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/03-notify-me-alias.md
 delete mode 100644 agent_skills/docs/plans/2026-08-22-xknvle9g-notify-skill-done/context/design.md
5e5d952a149eb813d0dac8e7d9401014fe4bc6a5
```

## 2026-09-05-20av91yc-ask-user-done

**Title:** ask-user skill

**Commit:** `rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/01-payload-contract.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/02-cli-io.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/03-wizard.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/04-skill-docs.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/context/design.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/context/pre_planning_session.md'
[main 666828e] docs(agent_skills): archive ask-user
 6 files changed, 536 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/01-payload-contract.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/02-cli-io.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/03-wizard.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/04-skill-docs.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/context/design.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/context/pre_planning_session.md
666828eab2b49b53e04c846dfb409cd6c41798f6`

Added the ask-user PySide6 wizard: stdin JSON questions, a blocking desktop picker, stdout answers, and exit 0/2/4/6. Open the diff for the payload contract, Qt-free module split, and the original fallback-only description that later plans inverted.

```bash
git show rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/01-payload-contract.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/02-cli-io.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/03-wizard.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/04-skill-docs.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/context/design.md'
rm 'agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/context/pre_planning_session.md'
[main 666828e] docs(agent_skills): archive ask-user
 6 files changed, 536 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/01-payload-contract.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/02-cli-io.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/03-wizard.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/04-skill-docs.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/context/design.md
 delete mode 100644 agent_skills/docs/plans/2026-09-05-20av91yc-ask-user-done/context/pre_planning_session.md
666828eab2b49b53e04c846dfb409cd6c41798f6
```

## 2026-09-10-jdmwc8j1-ask-user-ssh-done

**Title:** ask-user over SSH

**Commit:** `rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/01-ssh-detect.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/02-http-wizard.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/03-untun-bridge.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/04-skill-docs.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/context/design.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/context/pre_planning_session.md'
[main 2061b66] docs(agent_skills): archive ask-user-ssh
 6 files changed, 405 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/01-ssh-detect.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/02-http-wizard.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/03-untun-bridge.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/04-skill-docs.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/context/design.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/context/pre_planning_session.md
2061b660fda0fba78305359c1bdc09f5232cab5a`

Gave ask-user an SSH path that skips Qt, serves a tunneled 7.css wizard, and keeps the same JSON/exit contract. Open the diff for SSH detection, the unused fuse, the ask-user: URL line, and the untun/http_wizard split.

```bash
git show rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/01-ssh-detect.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/02-http-wizard.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/03-untun-bridge.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/04-skill-docs.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/context/design.md'
rm 'agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/context/pre_planning_session.md'
[main 2061b66] docs(agent_skills): archive ask-user-ssh
 6 files changed, 405 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/01-ssh-detect.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/02-http-wizard.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/03-untun-bridge.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/04-skill-docs.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/context/design.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-jdmwc8j1-ask-user-ssh-done/context/pre_planning_session.md
2061b660fda0fba78305359c1bdc09f5232cab5a
```

## 2026-09-10-t9uehccf-ask-user-vgd-done

**Title:** Shorten ask-user tunnel URLs with v.gd

**Commit:** `rm 'agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/01-vgd-client.md'
rm 'agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/02-wire-ssh.md'
rm 'agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/03-readme.md'
rm 'agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/context/design.md'
[main 9da50b2] docs(agent_skills): archive ask-user-vgd
 4 files changed, 221 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/01-vgd-client.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/02-wire-ssh.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/03-readme.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/context/design.md
9da50b2a20c8b6dc40973721de9534c7e0d0c1df`

POSTs the SSH wizard URL to v.gd and prints the short link on the existing ask-user: stderr line, falling back to the long Cloudflare URL on failure. Open the diff for the POST/parse/retry rules and the silent SKILL.md relay contract.

```bash
git show rm 'agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/01-vgd-client.md'
rm 'agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/02-wire-ssh.md'
rm 'agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/03-readme.md'
rm 'agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/context/design.md'
[main 9da50b2] docs(agent_skills): archive ask-user-vgd
 4 files changed, 221 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/01-vgd-client.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/02-wire-ssh.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/03-readme.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-t9uehccf-ask-user-vgd-done/context/design.md
9da50b2a20c8b6dc40973721de9534c7e0d0c1df
```

## 2026-09-10-uaxdn96i-ask-user-primary-done

**Title:** ask-user replaces the native questions tool

**Commit:** `rm 'agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/01-ask-user-routing.md'
rm 'agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/02-patch-consumers.md'
rm 'agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/03-write-adr.md'
rm 'agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/context/design.md'
[main b6be9c0] docs(agent_skills): archive ask-user-primary
 4 files changed, 247 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/01-ask-user-routing.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/02-patch-consumers.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/03-write-adr.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/context/design.md
b6be9c0f210fc94ae692dc44180778a3035dbd05`

Made ask-user the primary picker, patched six consumer skills, and recorded the invert as ADR 0001. Open the diff for the cannot-open fallback chain and the consumer ask-via-ask-user wording.

```bash
git show rm 'agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/01-ask-user-routing.md'
rm 'agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/02-patch-consumers.md'
rm 'agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/03-write-adr.md'
rm 'agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/context/design.md'
[main b6be9c0] docs(agent_skills): archive ask-user-primary
 4 files changed, 247 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/01-ask-user-routing.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/02-patch-consumers.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/03-write-adr.md
 delete mode 100644 agent_skills/docs/plans/2026-09-10-uaxdn96i-ask-user-primary-done/context/design.md
b6be9c0f210fc94ae692dc44180778a3035dbd05
```

## 2026-09-12-04fwnvsr-shorten-url-done

**Title:** Shorten-url skill

**Commit:** `rm 'agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/01-cli.md'
rm 'agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/02-skill.md'
rm 'agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/context/design.md'
[main cacbdad] docs(agent_skills): archive shorten-url
 3 files changed, 227 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/01-cli.md
 delete mode 100644 agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/02-skill.md
 delete mode 100644 agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/context/design.md
cacbdad9a3a72ae7a5c1d6a6dbc06609697d452f`

Added a shorten-url skill and uv CLI that POSTs one --url to v.gd, pass-throughs existing v.gd links, and fails loud with prefixed stderr logs. Open the diff for the retry/rate-limit wait and the agent invoke/timeout contract.

```bash
git show rm 'agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/01-cli.md'
rm 'agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/02-skill.md'
rm 'agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/context/design.md'
[main cacbdad] docs(agent_skills): archive shorten-url
 3 files changed, 227 deletions(-)
 delete mode 100644 agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/01-cli.md
 delete mode 100644 agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/02-skill.md
 delete mode 100644 agent_skills/docs/plans/2026-09-12-04fwnvsr-shorten-url-done/context/design.md
cacbdad9a3a72ae7a5c1d6a6dbc06609697d452f
```
