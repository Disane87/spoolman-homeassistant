module.exports = {
    plugins: [
        [
            "@semantic-release/commit-analyzer",
            {
                preset: "conventionalcommits",
                releaseRules: [
                    { type: "feat", release: "minor" },
                    { type: "fix", release: "patch" },
                    { type: "perf", release: "patch" },
                    { type: "docs", release: false },
                    { type: "refactor", release: false },
                    { type: "style", release: false },
                    { type: "test", release: false },
                    { type: "chore", release: false },
                    { type: "ci", release: false },
                    { type: "build", release: false }
                ]
            }
        ],
        [
            "@semantic-release/release-notes-generator",
            {
                preset: "conventionalcommits",
                presetConfig: {
                    types: [
                        { type: "feat", section: "🚀 Features" },
                        { type: "fix", section: "🛠️ Fixes" },
                        { type: "perf", section: "⏩ Performance" },
                        { type: "docs", section: "📔 Docs" },
                        { type: "refactor", section: "♻️ Refactor", hidden: true },
                        { type: "style", section: "💈 Style", hidden: true },
                        { type: "test", section: "🧪 Tests", hidden: true },
                        { type: "build", section: "🦊 CI/CD", hidden: true },
                        { type: "ci", section: "🦊 CI/CD", hidden: true },
                        { type: "chore", section: "🧹 Other", hidden: true }
                    ]
                },
                writerOpts: {
                    transform: (commit, context) => {
                        // Filter out merge commits
                        if (commit.subject && commit.subject.startsWith('Merge')) {
                            return null;
                        }

                        // Clone the commit object to avoid immutability issues
                        const transformedCommit = Object.assign({}, commit);

                        // Add contributor info
                        if (transformedCommit.author && transformedCommit.author.name) {
                            transformedCommit.authorName = transformedCommit.author.name;
                            transformedCommit.authorUrl = `https://github.com/${transformedCommit.author.name}`;
                        }

                        return transformedCommit;
                    },
                    commitPartial: '* {{#if scope}}**{{scope}}:** {{/if}}{{subject}}{{#if authorName}} ([@{{authorName}}]({{authorUrl}})){{/if}}{{#if hash}} ([{{hash}}]({{commitUrlFormat}})){{/if}}\n'
                }
            }
        ],
        [
            "@semantic-release/exec",
            {
                prepareCmd: "./scripts/publish.sh ${nextRelease.version} ${branch.name} ${commits.length} ${Date.now()}"
            }
        ],
        "@semantic-release/changelog",
        [
            "@semantic-release/git",
            {
                message: "chore(release): 📢 ${nextRelease.version}\n\n${nextRelease.notes}",
                assets: [
                    "hacs.json",
                    "CHANGELOG.md",
                    "README.md"
                ]
            }
        ],
        [
            "@semantic-release/github",
            {
                assets: [
                    "dist/*.zip"
                ],
                fail: true
            }
        ]
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
