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
                linkCompare: true,
                linkReferences: true,
                presetConfig: {
                    types: [
                        { type: "feat", section: "🚀 Features", hidden: false },
                        { type: "fix", section: "🛠️ Fixes", hidden: false },
                        { type: "perf", section: "⏩ Performance", hidden: false },
                        { type: "docs", section: "📔 Docs", hidden: false },
                        { type: "refactor", section: "♻️ Refactor", hidden: true },
                        { type: "style", section: "💈 Style", hidden: true },
                        { type: "test", section: "🧪 Tests", hidden: true },
                        { type: "build", section: "🦊 CI/CD", hidden: true },
                        { type: "ci", section: "🦊 CI/CD", hidden: true },
                        { type: "chore", section: "🧹 Other", hidden: true }
                    ]
                },
                writerOpts: {
                    groupBy: "type",
                    commitGroupsSort: "title",
                    commitsSort: ["scope", "subject"]
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
