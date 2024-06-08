# Contribution Guidelines

If you're a developer and want to contribute to the project, please feel free to create a Pull Request (PR)! However, there are some constraints that need to be enforced by convention (currently, I am evaluating the possibility of enforcing this by rules. If you have a good hint, please let me know 🎉):

## Branching Strategy

- **Please merge your PR to the `dev` branch.** PRs against `main` will be rejected.
- The `main` branch only reflects the latest state of the integration.
- The `dev` branch reflects the next state of the integration.

## Commit Messages

- **Please make use of conventional commits.** This ensures the build pipeline works together with semantic release, and your PRs will trigger a new release.

## Development Environment

- I recommend using Visual Studio Code as the development environment, since everything works out of the box.

## CI/CD Requirements

- Adhering to these guidelines is crucial because our CI/CD pipeline depends on this workflow. The `dev` branch is used for testing and validation, while `main` is reserved for stable releases.

## General Guidelines

1. **Code Quality:**
   - Ensure your code is clean, well-documented, and follows the project’s coding standards.
   - Write clear, concise, and descriptive comments where necessary.
   - Refactor code where needed to maintain readability and simplicity.

2. **Testing:**
   - Write unit tests for your code to ensure functionality.
   - Run all existing tests to make sure your changes do not break any existing functionality.
   - Ensure your code passes the CI tests before submitting a PR.

3. **Documentation:**
   - Update the documentation to reflect any changes in the code.
   - Ensure new features or changes are documented with examples and usage instructions.

4. **Issue Tracking:**
   - Reference any relevant issues in your commit messages and PR descriptions.
   - Use keywords like "fixes" or "closes" followed by the issue number to link PRs to issues.

5. **Code Reviews:**
   - Be responsive to feedback from code reviewers and make necessary changes promptly.
   - Review others' PRs if you have the expertise and provide constructive feedback.

6. **Style Guidelines:**
   - Follow the established coding style of the project. Consistency is key.
   - Use linting tools provided in the project to maintain code style.

7. **Communication:**
   - Be respectful and considerate in all communications.
   - Discuss any significant changes or new features with the project maintainers before starting work to ensure alignment with project goals.

## Thank You!

Thank you for contributing and helping to maintain the quality and consistency of the project!