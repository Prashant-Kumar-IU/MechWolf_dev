# Contributing to MechWolf

Thank you for your interest in contributing to MechWolf! We welcome contributions of all kinds.

## 🐛 Bug Reports

Found a bug? Please [open an issue](https://github.com/MechWolf/MechWolf/issues/new?template=bug_report.md) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, MechWolf version)

## 💡 Feature Requests

Have an idea? [Open a feature request](https://github.com/MechWolf/MechWolf/issues/new?template=feature_request.md) describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives considered

## 🔧 Code Contributions

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for new functionality
5. **Run** tests (`python -m pytest`)
6. **Commit** changes (`git commit -m 'Add amazing feature'`)
7. **Push** to branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

## 📝 Documentation

Help improve our docs by:
- Fixing typos or unclear explanations
- Adding examples
- Improving API documentation
- Creating tutorials

## 💻 Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/MechWolf.git
cd MechWolf

# Install in development mode
pip install -e .[dev]

# Run tests
python -m pytest
```

## 📋 Code Style

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for code formatting
- Add type hints where appropriate
- Write clear, descriptive commit messages

## ❓ Questions

Need help? Feel free to [open a discussion](https://github.com/MechWolf/MechWolf/discussions) or reach out to the maintainers.

## Get started

1. First, [fork the repository on GitHub](https://github.com/MechWolf/MechWolf).
1. Clone your fork:
   ```bash
   $ git clone git@github.com:your_name_here/MechWolf.git
   ```
1. Set up your virtualenv:
   ```bash
   $ virtualenv -p python3.7 mechwolf-dev-env
   $ source mechwolf-dev-env/bin/activate
   ```
1. Install MechWolf with the developer dependencies:
   ```bash
   (mechwolf-dev-env) $ cd MechWolf
   (mechwolf-dev-env) $ pip install -e .
   (mechwolf-dev-env) $ pip install -r requirements-dev.txt
   ```
1. Set up [pre-commit](https://pre-commit.com/):
   ```bash
   (mechwolf-dev-env) $ pre-commit install
   ```
1. Make a new branch:
   ```bash
   (mechwolf-dev-env) $ git checkout -b name-of-your-bugfix-or-feature
   ```
1. Once you're done making your changes, make sure that the test suite passes:
   ```bash
   (mechwolf-dev-env) $ pytest
   ```
1. Then, make your commit:
   ```bash
   (mechwolf-dev-env) $ git add *
   (mechwolf-dev-env) $ git commit -am "commit message here"
   (mechwolf-dev-env) $ git push origin name-of-your-bugfix-or-feature
   ```
   Pre-commit will make sure that your changes conform to our [coding style](https://github.com/python/black/), as well as that it passes some [static analysis tests](http://flake8.pycqa.org/en/latest/) and is [correctly typed](https://mypy.readthedocs.io/en/latest/).
1. When you're done, create a pull request for us to review.
   As a general request, please ensure that the tests and documentation are updated before submitting your pull request.
   This allows us to review and accept it as quickly as possible.
   Furthermore, it should be compatible with all supported Python versions, which is currently only Python 3.7.
