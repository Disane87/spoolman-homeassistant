module.exports = {
  plugins: [
    [
      "@semantic-release/commit-analyzer",
      {
        preset: "conventionalcommits",
        releaseRules: [
          {type: "feat", release: "minor"},
          {type: "fix", release: "patch"},
          {type: "perf", release: "patch"},
          {type: "docs", release: false},
          {type: "refactor", release: false},
          {type: "style", release: false},
          {type: "test", release: false},
          {type: "chore", release: false},
          {type: "ci", release: false},
          {type: "build", release: false}
        ]
      }
    ],
    [
      "@semantic-release/release-notes-generator",
      {
        preset: "conventionalcommits",
        presetConfig: {
          types: [
            {type: "feat", section: "🚀 Features"},
            {type: "fix", section: "🛠️ Fixes"},
            {type: "perf", section: "⏩ Performance"},
            {type: "docs", section: "📔 Docs"},
            {type: "refactor", section: "♻️ Refactor", hidden: true},
            {type: "style", section: "💈 Style", hidden: true},
            {type: "test", section: "🧪 Tests", hidden: true},
            {type: "build", section: "🦊 CI/CD", hidden: true},
            {type: "ci", section: "🦊 CI/CD", hidden: true},
            {type: "chore", section: "🧹 Other", hidden: true}
          ]
        },
        writerOpts: {
          transform: (commit, context) => {
            // Filter out merge commits
            if (commit.subject && commit.subject.startsWith('Merge')) {
              return null;
            }

            // Add contributor info
            if (commit.author && commit.author.name) {
              commit.authorName = commit.author.name;
              commit.authorUrl = `https://github.com/${commit.author.name}`;
            }

            return commit;
          },
          commitPartial: '* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}{{#if authorName}} ([@{{authorName}}]({{authorUrl}})){{/if}}{{#if hash}} ([{{hash}}]({{commitUrlFormat}})){{/if}}\n'
        }
      }
    ],
    "@semantic-release/changelog"
    // NOTE: @semantic-release/git and @semantic-release/github are intentionally excluded for dry-run testing
  ],
  branches: [
    "main",
    {
      name: "dev",
      prerelease: true,
      channel: "dev"
    }
  ]
};
