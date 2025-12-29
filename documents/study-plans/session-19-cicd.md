# Session 19: CI/CD Pipeline

**Phase:** 5 - Integration & Polish
**Estimated Duration:** 2-3 hours
**Difficulty:** Medium

---

## Prerequisites

- [ ] Session 18 complete (test suite ready)
- [ ] GitHub repository access
- [ ] Basic GitHub Actions knowledge (or willingness to learn)

---

## Learning Objectives

By the end of this session, you will understand:

1. **GitHub Actions** - workflow syntax, triggers, jobs
2. **ROS2 CI patterns** - Docker-based builds
3. **Test automation** - running tests on every push
4. **Status badges** - showing build status in README

---

## Practical Objectives

### Primary Goal
Set up GitHub Actions to automatically build and test the project on every push.

### Deliverables

1. **Create CI workflow:**
   - Triggers on push to main and PRs
   - Builds all packages
   - Runs all unit tests
   - Reports results

2. **Docker-based ROS2 CI:**
   - Use official ROS2 Docker image
   - Install dependencies
   - Build and test

3. **Add status badge:**
   - Build status in README
   - Visible pass/fail indication

4. **Document CI process:**
   - How to interpret failures
   - How to run locally

---

## Session Structure

| Time | Activity |
|------|----------|
| 0:00-0:30 | Study GitHub Actions syntax, ROS2 CI examples |
| 0:30-1:15 | Create workflow file |
| 1:15-1:45 | Test workflow (push, watch results) |
| 1:45-2:15 | Debug and fix issues |
| 2:15-2:30 | Add status badge to README |
| 2:30-3:00 | Document CI, commit |

---

## Verification Checklist

```bash
# 1. Workflow file exists
cat .github/workflows/ci.yml

# 2. Push triggers build
git push origin main
# Check Actions tab on GitHub

# 3. Build succeeds
# Green checkmark on commit

# 4. Tests run
# Test results in action logs

# 5. Badge shows in README
# Visit GitHub repo, check README renders badge
```

---

## Key Questions to Answer During Session

1. What base Docker image for ROS2 Humble?
2. How to cache dependencies for faster builds?
3. Should SITL tests run in CI? (Probably not - too heavy)
4. How to handle secrets/credentials? (Not needed for this)

---

## GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    container:
      image: ros:humble

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install dependencies
        run: |
          apt-get update
          apt-get install -y python3-pip python3-pytest python3-pytest-cov
          pip3 install python-statemachine py_trees

      - name: Setup ROS2 workspace
        run: |
          mkdir -p /ros_ws/src
          cp -r . /ros_ws/src/sh-uav-platform
          cd /ros_ws
          source /opt/ros/humble/setup.bash
          rosdep update
          rosdep install --from-paths src --ignore-src -r -y

      - name: Build packages
        run: |
          cd /ros_ws
          source /opt/ros/humble/setup.bash
          colcon build --symlink-install

      - name: Run tests
        run: |
          cd /ros_ws
          source /opt/ros/humble/setup.bash
          source install/setup.bash
          colcon test
          colcon test-result --verbose

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test-results
          path: /ros_ws/build/*/test_results/
```

---

## Caching Dependencies (Optimization)

```yaml
      - name: Cache ROS dependencies
        uses: actions/cache@v3
        with:
          path: /opt/ros
          key: ros-humble-${{ hashFiles('**/package.xml') }}

      - name: Cache pip packages
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('**/requirements.txt') }}
```

---

## README Badge

```markdown
# SH-UAV-Platform

![CI](https://github.com/Shadow-Harvest/sh-uav-platform/actions/workflows/ci.yml/badge.svg)

Autonomous UAV platform for visual target detection and approach.
```

---

## Potential Blockers

| Issue | Symptom | Resolution |
|-------|---------|------------|
| Docker image pull fails | Timeout | Retry, or use different registry |
| rosdep fails | Missing dependencies | Check package.xml completeness |
| Tests fail in CI but pass locally | Environment difference | Check Python version, deps |
| Workflow syntax error | Job doesn't start | Validate YAML syntax |

---

## Code Locations

- Workflow: `.github/workflows/ci.yml`
- README badge: `README.md`
- CI docs: `documents/contributing/ci.md`

---

## Definition of Done

- [ ] CI workflow file created
- [ ] Workflow triggers on push
- [ ] Build succeeds in CI
- [ ] Tests run in CI
- [ ] Status badge added to README
- [ ] CI process documented
- [ ] Committed with descriptive message

---

## Notes for Next Session

Session 20 will focus on documentation, code cleanup, and creating portfolio-ready materials.
