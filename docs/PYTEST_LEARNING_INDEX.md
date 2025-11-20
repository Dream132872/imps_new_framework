# Complete pytest & pytest-django Learning Guide

## 📚 Learning Path Overview

This is a comprehensive, sequential guide to learning pytest and pytest-django from absolute beginner to advanced level. The content is organized into multiple files that you can read in order, or jump to specific topics.

**If your internet breaks, you can continue from where you left off by checking the file you were reading.**

---

## 🗺️ Learning Sequence

### **Part 1: Foundations** (Start Here)
1. **[PYTEST_01_INTRODUCTION.md](PYTEST_01_INTRODUCTION.md)** - What is pytest, why use it, installation, basic concepts
2. **[PYTEST_02_BASICS.md](PYTEST_02_BASICS.md)** - Writing your first tests, assertions, test discovery, running tests
3. **[PYTEST_03_PYTEST_DJANGO_SETUP.md](PYTEST_03_PYTEST_DJANGO_SETUP.md)** - pytest-django setup, configuration, database access

### **Part 2: Core Concepts**
4. **[PYTEST_04_FIXTURES.md](PYTEST_04_FIXTURES.md)** - Fixtures deep dive: creation, scopes, dependencies, autouse, conftest
5. **[PYTEST_05_MARKERS_PARAMETRIZATION.md](PYTEST_05_MARKERS_PARAMETRIZATION.md)** - Markers, parametrization, filtering tests
6. **[PYTEST_06_MOCKING_BASICS.md](PYTEST_06_MOCKING_BASICS.md)** - Introduction to mocking, unittest.mock, MagicMock, Mock

### **Part 3: Testing Patterns**
7. **[PYTEST_07_TESTING_PATTERNS.md](PYTEST_07_TESTING_PATTERNS.md)** - AAA pattern, testing exceptions, edge cases, test organization
8. **[PYTEST_08_UNIT_TESTING.md](PYTEST_08_UNIT_TESTING.md)** - Unit testing principles, isolation, mocking strategies, domain layer testing
9. **[PYTEST_09_INTEGRATION_TESTING.md](PYTEST_09_INTEGRATION_TESTING.md)** - Integration testing, database tests, repository testing, real dependencies

### **Part 4: Advanced Topics**
10. **[PYTEST_10_ADVANCED_FIXTURES.md](PYTEST_10_ADVANCED_FIXTURES.md)** - Advanced fixtures, parametrized fixtures, fixture factories, dynamic fixtures
11. **[PYTEST_11_ADVANCED_MOCKING.md](PYTEST_11_ADVANCED_MOCKING.md)** - Advanced mocking, patching, side effects, spies, stubs
12. **[PYTEST_12_PYTEST_DJANGO_ADVANCED.md](PYTEST_12_PYTEST_DJANGO_ADVANCED.md)** - Advanced pytest-django: transactions, factories, test client, custom settings

### **Part 5: Best Practices & Real-World**
13. **[PYTEST_13_BEST_PRACTICES.md](PYTEST_13_BEST_PRACTICES.md)** - Best practices, test organization, naming conventions, maintainability
14. **[PYTEST_14_REAL_WORLD_EXAMPLES.md](PYTEST_14_REAL_WORLD_EXAMPLES.md)** - Real examples from your codebase, DDD testing, CQRS testing
15. **[PYTEST_15_DEBUGGING_TROUBLESHOOTING.md](PYTEST_15_DEBUGGING_TROUBLESHOOTING.md)** - Debugging tests, common issues, troubleshooting, performance

### **Part 6: Reference & Cheat Sheets**
16. **[PYTEST_16_REFERENCE_CHEATSHEET.md](PYTEST_16_REFERENCE_CHEATSHEET.md)** - Quick reference, command cheat sheet, common patterns
17. **[PYTEST_17_EXERCISES.md](PYTEST_17_EXERCISES.md)** - Practice exercises with solutions

---

## 🎯 How to Use This Guide

### For Complete Beginners
**Read in order:**
1. Start with `PYTEST_01_INTRODUCTION.md`
2. Follow the sequence 01 → 02 → 03 → ... → 17
3. Each file builds on the previous one
4. Practice the examples as you go

### For Quick Reference
- Jump to specific topics using the index above
- Use `PYTEST_16_REFERENCE_CHEATSHEET.md` for quick lookups
- Check `PYTEST_17_EXERCISES.md` for practice

### If Internet Breaks
1. Note which file number you were reading (e.g., "PYTEST_05")
2. When you return, continue from that file
3. Each file is self-contained but references previous concepts
4. Review previous files if you need a refresher

---

## 📋 What You'll Learn

### Core Skills
- ✅ Writing effective pytest tests
- ✅ Using fixtures for test setup
- ✅ Mocking and test doubles
- ✅ Unit testing principles
- ✅ Integration testing with Django
- ✅ Testing Django models, views, and APIs
- ✅ Testing DDD/CQRS architectures
- ✅ Test organization and structure

### Advanced Skills
- ✅ Advanced fixture patterns
- ✅ Parametrization strategies
- ✅ Custom markers and plugins
- ✅ Parallel test execution
- ✅ Coverage analysis
- ✅ Debugging and troubleshooting
- ✅ Performance optimization
- ✅ CI/CD integration

---

## 🛠️ Prerequisites

Before starting, make sure you have:
- Python 3.8+ installed
- Basic Python knowledge
- Basic Django knowledge
- Your project set up (IMPS_NEW_FRAMEWORK)
- pytest and pytest-django installed (already in your requirements.txt)

---

## 📦 Your Current Setup

Based on your `pytest.ini` and `requirements.txt`:

```ini
# Installed packages
pytest==8.0.0
pytest-django==4.8.0
pytest-xdist          # Parallel execution
pytest-cov            # Coverage
pytest-sugar          # Better output
factory-boy==3.3.0    # Test data factories
coverage==7.4.1       # Coverage tool
```

```ini
# Your pytest.ini configuration
DJANGO_SETTINGS_MODULE = config.settings
testpaths = src
pythonpath = src
addopts = --strict-markers --tb=long -vv -n 4 --create-db --color yes -rA
```

---

## 🚀 Quick Start

1. **Read**: `PYTEST_01_INTRODUCTION.md`
2. **Run your first test**: `pytest src/media/tests/domain/test_picture_entity.py -v`
3. **Continue sequentially** through the files
4. **Practice** with exercises in `PYTEST_17_EXERCISES.md`

---

## 📝 Progress Tracking

As you complete each section, you can check it off:

- [ ] Part 1: Foundations (Files 01-03)
- [ ] Part 2: Core Concepts (Files 04-06)
- [ ] Part 3: Testing Patterns (Files 07-09)
- [ ] Part 4: Advanced Topics (Files 10-12)
- [ ] Part 5: Best Practices & Real-World (Files 13-15)
- [ ] Part 6: Reference & Cheat Sheets (Files 16-17)

---

## 💡 Tips for Learning

1. **Read sequentially** - Each file builds on previous concepts
2. **Run examples** - Don't just read, execute the code
3. **Modify examples** - Try changing them to see what happens
4. **Look at your codebase** - Reference your existing tests in `src/media/tests/`
5. **Practice regularly** - Write tests for your own code
6. **Take breaks** - Each file is a good stopping point

---

## 🔗 Related Resources

- [Official pytest Documentation](https://docs.pytest.org/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)
- [Your existing test files](src/media/tests/)
- [HOW_TO_RUN_TESTS.md](src/media/tests/HOW_TO_RUN_TESTS.md)

---

## 📞 Need Help?

If you get stuck:
1. Re-read the relevant section
2. Check the reference cheat sheet
3. Look at examples in your codebase
4. Review previous files for context

---

**Ready to start?** → Begin with [PYTEST_01_INTRODUCTION.md](PYTEST_01_INTRODUCTION.md)

