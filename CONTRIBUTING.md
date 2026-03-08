# Contributing to Socratic Survey Chat

Thank you for your interest in contributing to this project. This document outlines the process for contributing.

## Getting Started

1. **Fork** the repository on GitHub.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/socratic-survey-chat.git
   cd socratic-survey-chat
   ```
3. **Set up the development environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Making Changes

- Follow the existing code style and conventions.
- Write clear, descriptive commit messages.
- Add tests for new functionality where applicable.
- Update documentation if your changes affect usage or setup.

## Pull Request Process

1. Ensure your changes pass any existing tests:
   ```bash
   pytest tests/
   ```
2. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
3. Open a pull request against the `main` branch of the upstream repository.
4. In your PR description, explain:
   - What the change does
   - Why it is needed
   - How it was tested

## Reporting Issues

- Use the [GitHub Issues](https://github.com/YannJY02/socratic-survey-chat/issues) page.
- Include steps to reproduce, expected behavior, and actual behavior.
- Provide your Python version, OS, and any relevant configuration details.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you agree to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the [AGPL-3.0 License](LICENSE).
