# Contributing

Thanks for improving CI Health Monitor.

1. Fork the repository and create a focused branch.
2. Use Python 3.10+ and keep runtime dependencies at zero unless a strong need is documented.
3. Add or update tests for behavioral changes.
4. Run `python -m unittest discover -s tests -v` and `python -m compileall -q src tests`.
5. Keep README examples synchronized with actual CLI behavior.
6. Do not commit real private CI exports, tokens, repository secrets, or generated build artifacts.
7. Open a pull request explaining the problem, approach, and validation performed.

Small, reviewable changes are preferred. By contributing, you agree that your contribution is provided under the repository's MIT License.