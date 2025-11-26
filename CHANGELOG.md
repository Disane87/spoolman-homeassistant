## [1.1.0-dev.3](https://github.com/Disane87/spoolman-homeassistant/compare/v1.1.0-dev.2...v1.1.0-dev.3) (2025-11-26)

### 🚀 Features

* **sensor:** add Spool Flow Rate sensor and integrate into setup ([e6f6636](https://github.com/Disane87/spoolman-homeassistant/commit/e6f66361962b63fbad06f99d14d9015d493ef8a2)), closes [#35](https://github.com/Disane87/spoolman-homeassistant/issues/35)

## [1.1.0-dev.2](https://github.com/Disane87/spoolman-homeassistant/compare/v1.1.0-dev.1...v1.1.0-dev.2) (2025-11-26)

### 🛠️ Fixes

* **sensor:** prevent IndexError and improve coordinator refresh behavior ([a079ae0](https://github.com/Disane87/spoolman-homeassistant/commit/a079ae0ff39afd57df557c350bf8bfdf5bce409d)), closes [#198](https://github.com/Disane87/spoolman-homeassistant/issues/198) [#125](https://github.com/Disane87/spoolman-homeassistant/issues/125) [#203](https://github.com/Disane87/spoolman-homeassistant/issues/203) [#141](https://github.com/Disane87/spoolman-homeassistant/issues/141)

## [1.1.0-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v1.0.0...v1.1.0-dev.1) (2025-11-26)

### 🛠️ Fixes

* resolve IndexError on auto-update and add immediate refresh after service calls ([de0f831](https://github.com/Disane87/spoolman-homeassistant/commit/de0f831221132473478cdf01e61a58ede2cf2924)), closes [#198](https://github.com/Disane87/spoolman-homeassistant/issues/198) [#125](https://github.com/Disane87/spoolman-homeassistant/issues/125)
* **api:** remove timeout parameter to match existing API patterns ([b3e0015](https://github.com/Disane87/spoolman-homeassistant/commit/b3e001585b17745da93a9a0f81de82fbf7ccdafb))
* **sensor:** update spool entity data access for new coordinator structure ([f26a202](https://github.com/Disane87/spoolman-homeassistant/commit/f26a202ddd6a3edd4aa7ff02069d260ed9a1e8a6))

### 📔 Docs

* document the `spoolman.use_spool_filament` service ([e6c4b13](https://github.com/Disane87/spoolman-homeassistant/commit/e6c4b13fe2b4fea8f1e1500f0c380d3534eba18e))
* document the `spoolman.use_spool_filament` service ([1401cf0](https://github.com/Disane87/spoolman-homeassistant/commit/1401cf0a5986b830a4e92a11d37ae7a7058a4186)), closes [#261](https://github.com/Disane87/spoolman-homeassistant/issues/261)
* document the `spoolman.use_spool_filament` service ([45821e3](https://github.com/Disane87/spoolman-homeassistant/commit/45821e371d41b152ed3a2fbc4312cf3d81423c51))

### 🚀 Features

* **api:** add get_filaments method to SpoolmanAPI ([e162c1a](https://github.com/Disane87/spoolman-homeassistant/commit/e162c1a340c2a1a29d2ba2f5569c2f05694521e8))
* **coordinator:** add filament data processing and aggregation ([758c608](https://github.com/Disane87/spoolman-homeassistant/commit/758c60810408341e8dbdd617b52f9d648ae22aa5))
* **sensor:** add Filament sensor class and image generation ([1b6fd6e](https://github.com/Disane87/spoolman-homeassistant/commit/1b6fd6ec5307a7a35c701ac04f2e3b37a9636f6c))
* **sensor:** integrate filament entities in async_setup_entry ([d1ad539](https://github.com/Disane87/spoolman-homeassistant/commit/d1ad5394948343eb6d078f303877c5f3c6899d53))

## [1.0.0-dev.3](https://github.com/Disane87/spoolman-homeassistant/compare/v1.0.0-dev.2...v1.0.0-dev.3) (2025-11-26)

### 🛠️ Fixes

* **api:** remove timeout parameter to match existing API patterns ([b3e0015](https://github.com/Disane87/spoolman-homeassistant/commit/b3e001585b17745da93a9a0f81de82fbf7ccdafb))
* **sensor:** update spool entity data access for new coordinator structure ([f26a202](https://github.com/Disane87/spoolman-homeassistant/commit/f26a202ddd6a3edd4aa7ff02069d260ed9a1e8a6))

### 🚀 Features

* **api:** add get_filaments method to SpoolmanAPI ([e162c1a](https://github.com/Disane87/spoolman-homeassistant/commit/e162c1a340c2a1a29d2ba2f5569c2f05694521e8))
* **coordinator:** add filament data processing and aggregation ([758c608](https://github.com/Disane87/spoolman-homeassistant/commit/758c60810408341e8dbdd617b52f9d648ae22aa5))
* **sensor:** add Filament sensor class and image generation ([1b6fd6e](https://github.com/Disane87/spoolman-homeassistant/commit/1b6fd6ec5307a7a35c701ac04f2e3b37a9636f6c))
* **sensor:** integrate filament entities in async_setup_entry ([d1ad539](https://github.com/Disane87/spoolman-homeassistant/commit/d1ad5394948343eb6d078f303877c5f3c6899d53))

## [1.0.0](https://github.com/Disane87/spoolman-homeassistant/compare/v0.7.0...v1.0.0) (2025-03-09)

### ⚠ BREAKING CHANGES

* Generation of spoolnames was fixed. It now has a preffix "spoolman_*" to avoid conflicts with other spoolnames and only tthe ID of the spool is used as a suffix. This means that the spoolname is now unique and can be used to identify the spool in the spoolman. This needs a reconfiguration of the integration and adjustsments in automation when spools are used.

### 🛠️ Fixes

* Added paragraph about naming of the entity ids in the README ([0b9fc06](https://github.com/Disane87/spoolman-homeassistant/commit/0b9fc0637f74de9af022350ba7a700c6d46de38a)), closes [#170](https://github.com/Disane87/spoolman-homeassistant/issues/170)
* Iimproved logging for missing attributes ([dc05936](https://github.com/Disane87/spoolman-homeassistant/commit/dc0593651606d55081555553faa9b39b99e02d1e)), closes [#192](https://github.com/Disane87/spoolman-homeassistant/issues/192) [#170](https://github.com/Disane87/spoolman-homeassistant/issues/170)
* improve error handling in SpoolManCoordinator for API calls ([efeebea](https://github.com/Disane87/spoolman-homeassistant/commit/efeebeaa823046d013ca44b7b5c6f701e38557de)), closes [#177](https://github.com/Disane87/spoolman-homeassistant/issues/177)

### 🚀 Features

* Adds ability to change extra fields in spoolman ([007fda0](https://github.com/Disane87/spoolman-homeassistant/commit/007fda0ab38327ea1c8875cc2bbb63867cff4ae7))

## [1.0.0-dev.2](https://github.com/Disane87/spoolman-homeassistant/compare/v1.0.0-dev.1...v1.0.0-dev.2) (2025-03-09)

### 🛠️ Fixes

* Added paragraph about naming of the entity ids in the README ([0b9fc06](https://github.com/Disane87/spoolman-homeassistant/commit/0b9fc0637f74de9af022350ba7a700c6d46de38a)), closes [#170](https://github.com/Disane87/spoolman-homeassistant/issues/170)

## [1.0.0-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.8.0-dev.1...v1.0.0-dev.1) (2025-03-09)

### ⚠ BREAKING CHANGES

* Generation of spoolnames was fixed. It now has a preffix "spoolman_*" to avoid conflicts with other spoolnames and only tthe ID of the spool is used as a suffix. This means that the spoolname is now unique and can be used to identify the spool in the spoolman. This needs a reconfiguration of the integration and adjustsments in automation when spools are used.

### 🛠️ Fixes

* Iimproved logging for missing attributes ([dc05936](https://github.com/Disane87/spoolman-homeassistant/commit/dc0593651606d55081555553faa9b39b99e02d1e)), closes [#192](https://github.com/Disane87/spoolman-homeassistant/issues/192) [#170](https://github.com/Disane87/spoolman-homeassistant/issues/170)

## [0.8.0-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.7.0...v0.8.0-dev.1) (2025-03-05)

### 🚀 Features

* Adds ability to change extra fields in spoolman ([007fda0](https://github.com/Disane87/spoolman-homeassistant/commit/007fda0ab38327ea1c8875cc2bbb63867cff4ae7))

### 🛠️ Fixes

* improve error handling in SpoolManCoordinator for API calls ([efeebea](https://github.com/Disane87/spoolman-homeassistant/commit/efeebeaa823046d013ca44b7b5c6f701e38557de)), closes [#177](https://github.com/Disane87/spoolman-homeassistant/issues/177)

## [0.7.0-dev.3](https://github.com/Disane87/spoolman-homeassistant/compare/v0.7.0-dev.2...v0.7.0-dev.3) (2025-01-13)

### 🛠️ Fixes

* improve error handling in SpoolManCoordinator for API calls ([efeebea](https://github.com/Disane87/spoolman-homeassistant/commit/efeebeaa823046d013ca44b7b5c6f701e38557de)), closes [#177](https://github.com/Disane87/spoolman-homeassistant/issues/177)

## [0.7.0-dev.2](https://github.com/Disane87/spoolman-homeassistant/compare/v0.7.0-dev.1...v0.7.0-dev.2) (2024-12-16)

### 🚀 Features

* added longitudinal color ([d2f2809](https://github.com/Disane87/spoolman-homeassistant/commit/d2f28098d6ebb169a7c9a0fb1e55685cc7d305a7)), closes [#150](https://github.com/Disane87/spoolman-homeassistant/issues/150)

## [0.7.0-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.6.0...v0.7.0-dev.1) (2024-12-16)

### 🚀 Features

* added multicolor images for multicolor filaments ([bbd7025](https://github.com/Disane87/spoolman-homeassistant/commit/bbd7025a4f09784d741d0d94cf5604bf911df3d2)), closes [#150](https://github.com/Disane87/spoolman-homeassistant/issues/150)

## [0.6.0](https://github.com/Disane87/spoolman-homeassistant/compare/v0.5.0...v0.6.0) (2024-12-16)

### 🚀 Features

* add `use_spool_filament` service ([6602e4a](https://github.com/Disane87/spoolman-homeassistant/commit/6602e4a046a723b415c05342c391dbca16491542))

### 📔 Docs

* update example spool ID ([70e6ed8](https://github.com/Disane87/spoolman-homeassistant/commit/70e6ed8e2f7094f130bb645e59bef241a4496e98))

## [0.5.0](https://github.com/Disane87/spoolman-homeassistant/compare/v0.4.3...v0.5.0) (2024-07-02)

### 🛠️ Fixes

* added names for service.yaml ([2f9801e](https://github.com/Disane87/spoolman-homeassistant/commit/2f9801e34b8ccda20c469bd45f7baaf2929da567))
* Fix blocking of entity picture generation ([6f54177](https://github.com/Disane87/spoolman-homeassistant/commit/6f541777a3799d3b694753ec5cc3f63e3bac850b)), closes [#121](https://github.com/Disane87/spoolman-homeassistant/issues/121)
* removed periods from descriptions and names ([6b821b6](https://github.com/Disane87/spoolman-homeassistant/commit/6b821b6f9b06fc53502a20b4cca2b9c079775cc7)), closes [#119](https://github.com/Disane87/spoolman-homeassistant/issues/119)

### 🚀 Features

* service integration to change a spool in Spoolman via API ([881a76b](https://github.com/Disane87/spoolman-homeassistant/commit/881a76bf5e149a3917b3cfd1041ca01a2d1fafd9)), closes [#119](https://github.com/Disane87/spoolman-homeassistant/issues/119)

### 📔 Docs

* changed CONTRIBUTING.md ([144c4e2](https://github.com/Disane87/spoolman-homeassistant/commit/144c4e2d9f8916a8aa2bafbfffe898b048aa2ea0))

## [0.5.0-dev.2](https://github.com/Disane87/spoolman-homeassistant/compare/v0.5.0-dev.1...v0.5.0-dev.2) (2024-07-01)

### 🛠️ Fixes

* removed periods from descriptions and names ([6b821b6](https://github.com/Disane87/spoolman-homeassistant/commit/6b821b6f9b06fc53502a20b4cca2b9c079775cc7)), closes [#119](https://github.com/Disane87/spoolman-homeassistant/issues/119)

## [0.5.0-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.4.4-dev.1...v0.5.0-dev.1) (2024-07-01)

### 🛠️ Fixes

* added names for service.yaml ([2f9801e](https://github.com/Disane87/spoolman-homeassistant/commit/2f9801e34b8ccda20c469bd45f7baaf2929da567))

### 🚀 Features

* service integration to change a spool in Spoolman via API ([881a76b](https://github.com/Disane87/spoolman-homeassistant/commit/881a76bf5e149a3917b3cfd1041ca01a2d1fafd9)), closes [#119](https://github.com/Disane87/spoolman-homeassistant/issues/119)

## [0.4.4-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.4.3...v0.4.4-dev.1) (2024-06-09)

### 🛠️ Fixes

* Fix blocking of entity picture generation ([6f54177](https://github.com/Disane87/spoolman-homeassistant/commit/6f541777a3799d3b694753ec5cc3f63e3bac850b)), closes [#121](https://github.com/Disane87/spoolman-homeassistant/issues/121)

### 📔 Docs

* changed CONTRIBUTING.md ([144c4e2](https://github.com/Disane87/spoolman-homeassistant/commit/144c4e2d9f8916a8aa2bafbfffe898b048aa2ea0))

## [0.4.3](https://github.com/Disane87/spoolman-homeassistant/compare/v0.4.2...v0.4.3) (2024-04-01)


### 🛠️ Fixes

* Fixes an issue when there is no active spool in klipper ([eda5f32](https://github.com/Disane87/spoolman-homeassistant/commit/eda5f329dd7708c2b2e997923acc7f966cd6504e)), closes [#105](https://github.com/Disane87/spoolman-homeassistant/issues/105)

## [0.4.2-dev.2](https://github.com/Disane87/spoolman-homeassistant/compare/v0.4.2-dev.1...v0.4.2-dev.2) (2024-03-30)

### 🛠️ Fixes
* Fixes an issue when there is no active spool in klipper ([eda5f32](https://github.com/Disane87/spoolman-homeassistant/commit/eda5f329dd7708c2b2e997923acc7f966cd6504e)), closes [#105](https://github.com/Disane87/spoolman-homeassistant/issues/105)


## [0.4.2](https://github.com/Disane87/spoolman-homeassistant/compare/v0.4.1...v0.4.2) (2024-03-18)
### 🛠️ Fixes
* :bug: Fixes a bug where klipper url wasn't checked correctly which leads to an exception ([441e4e5](https://github.com/Disane87/spoolman-homeassistant/commit/441e4e58ec25143fe7f0b0989d61c08b5168864f)), closes [#100](https://github.com/Disane87/spoolman-homeassistant/issues/100)

## [0.4.2-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.4.1...v0.4.2-dev.1) (2024-03-18)


### 🛠️ Fixes

* :bug: Fixes a bug where klipper url wasn't checked correctly which leads to an exception ([441e4e5](https://github.com/Disane87/spoolman-homeassistant/commit/441e4e58ec25143fe7f0b0989d61c08b5168864f)), closes [#100](https://github.com/Disane87/spoolman-homeassistant/issues/100)

## [0.4.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.4.0...v0.4.1) (2024-03-08)


### 🛠️ Fixes

* Fix key access to possibly non-existent location ([7e3a016](https://github.com/Disane87/spoolman-homeassistant/commit/7e3a0166b2354c9ecf83cc1d3a3fc5d5a28dbb3b))
* Fix key access to possibly non-existent location ([0f5f810](https://github.com/Disane87/spoolman-homeassistant/commit/0f5f810749a731773ef16ad5e3ab6aa07fa7c639))


### 📔 Docs

* Update README.md ([3b696dd](https://github.com/Disane87/spoolman-homeassistant/commit/3b696dd39d55a3a72121e7f29c5a6504acf1c130))

## [0.4.1-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.4.0...v0.4.1-dev.1) (2024-03-08)


### 🛠️ Fixes

* Fix key access to possibly non-existent location ([7e3a016](https://github.com/Disane87/spoolman-homeassistant/commit/7e3a0166b2354c9ecf83cc1d3a3fc5d5a28dbb3b))


### 📔 Docs

* Update README.md ([3b696dd](https://github.com/Disane87/spoolman-homeassistant/commit/3b696dd39d55a3a72121e7f29c5a6504acf1c130))

## [0.4.0](https://github.com/Disane87/spoolman-homeassistant/compare/v0.3.1...v0.4.0) (2024-03-06)


### 🚀 Features

* :sparkles: Added an attribute `klipper_active_spool` for spools which are active in Klipper (if Klipper url is provided in the config) ([0bd66f1](https://github.com/Disane87/spoolman-homeassistant/commit/0bd66f1673a6697c65e9ce03fd0c631258d81071)), closes [#86](https://github.com/Disane87/spoolman-homeassistant/issues/86)

## [0.4.0-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.3.1...v0.4.0-dev.1) (2024-03-06)


### 🚀 Features

* :sparkles: Added an attribute `klipper_active_spool` for spools which are active in Klipper (if Klipper url is provided in the config) ([0bd66f1](https://github.com/Disane87/spoolman-homeassistant/commit/0bd66f1673a6697c65e9ce03fd0c631258d81071)), closes [#86](https://github.com/Disane87/spoolman-homeassistant/issues/86)

## [0.3.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.3.0...v0.3.1) (2024-03-06)


### 🛠️ Fixes

* Bugfix for broken config flow ([24b329e](https://github.com/Disane87/spoolman-homeassistant/commit/24b329e5ffa6d8077c8f7b70a85d7f7fbd7e68b7)), closes [#84](https://github.com/Disane87/spoolman-homeassistant/issues/84)
* Proper stale bot config ([c47a1a4](https://github.com/Disane87/spoolman-homeassistant/commit/c47a1a4fc066b870899d97f362dd913ebc7b57e8))

## [0.3.0-dev.5](https://github.com/Disane87/spoolman-homeassistant/compare/v0.3.0-dev.4...v0.3.0-dev.5) (2024-03-06)


### 🛠️ Fixes

* Bugfix for broken config flow ([24b329e](https://github.com/Disane87/spoolman-homeassistant/commit/24b329e5ffa6d8077c8f7b70a85d7f7fbd7e68b7)), closes [#84](https://github.com/Disane87/spoolman-homeassistant/issues/84)
* fixed errors in automation example and added badges for achived spools in card examples ([bb36191](https://github.com/Disane87/spoolman-homeassistant/commit/bb36191ea59a14312c61ba4eb4b998bd264ac09b))
* Proper stale bot config ([c47a1a4](https://github.com/Disane87/spoolman-homeassistant/commit/c47a1a4fc066b870899d97f362dd913ebc7b57e8))

## [0.3.0-dev.4](https://github.com/Disane87/spoolman-homeassistant/compare/v0.3.0-dev.3...v0.3.0-dev.4) (2024-03-05)


### 🚀 Features

* :sparkles: Configuration of Entry can be edited later (to change values like `update_interval`) ([ed201f9](https://github.com/Disane87/spoolman-homeassistant/commit/ed201f9a35ea6f4aea49fdda1e27b4ec122071e4)), closes [#82](https://github.com/Disane87/spoolman-homeassistant/issues/82)

## [0.3.0-dev.3](https://github.com/Disane87/spoolman-homeassistant/compare/v0.3.0-dev.2...v0.3.0-dev.3) (2024-03-04)


### 🛠️ Fixes

* :bug: Fixed a bug where `used_weight` is empty sometimes ([03ce8fc](https://github.com/Disane87/spoolman-homeassistant/commit/03ce8fc133713b5a5be70b5acfce02740a323b38)), closes [#77](https://github.com/Disane87/spoolman-homeassistant/issues/77)

## [0.3.0-dev.2](https://github.com/Disane87/spoolman-homeassistant/compare/v0.3.0-dev.1...v0.3.0-dev.2) (2024-02-06)


### 🛠️ Fixes

* :bug: Refactor debug log message for filament weight calculation ([956e5ba](https://github.com/Disane87/spoolman-homeassistant/commit/956e5bac8f94de2b0f4eba73ba2b2d44ba54e37f)), closes [#77](https://github.com/Disane87/spoolman-homeassistant/issues/77)

## [0.3.0-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.2-dev.3...v0.3.0-dev.1) (2024-02-06)


### 🚀 Features

* :bug: Add debug logging for spool information ([df84521](https://github.com/Disane87/spoolman-homeassistant/commit/df845215c0a90bd1f12f60866de8b02d0d1c0ed3)), closes [#77](https://github.com/Disane87/spoolman-homeassistant/issues/77)

## [0.2.2-dev.3](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.2-dev.2...v0.2.2-dev.3) (2024-02-06)
=======
## [0.2.2](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.1...v0.2.2) (2023-11-02)



### 🛠️ Fixes

* :bug: Refactor SpoolmanAPI and SpoolManCoordinator warnings ([b1c0cb8](https://github.com/Disane87/spoolman-homeassistant/commit/b1c0cb82487cc1a2895ee1944becfedf9c90b394)), closes [#77](https://github.com/Disane87/spoolman-homeassistant/issues/77)

## [0.2.2-dev.2](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.2-dev.1...v0.2.2-dev.2) (2023-12-08)


### 🛠️ Fixes

* Better handling of null values ([aa0d763](https://github.com/Disane87/spoolman-homeassistant/commit/aa0d7636d69ccd87fe4be1feba90b4c69cc50858)), closes [#61](https://github.com/Disane87/spoolman-homeassistant/issues/61) [#58](https://github.com/Disane87/spoolman-homeassistant/issues/58)


### 📔 Docs

* added usage of entities in cards to readme ([c99262f](https://github.com/Disane87/spoolman-homeassistant/commit/c99262f452e82c8f7da0c89cf5d2385c919aaca2)), closes [#62](https://github.com/Disane87/spoolman-homeassistant/issues/62)
=======
* :bug: fixed a bug where location from spoolman is empty ([8ce5abd](https://github.com/Disane87/spoolman-homeassistant/commit/8ce5abd6a90b77ab4f233305ae5475623c042aa0)), closes [#44](https://github.com/Disane87/spoolman-homeassistant/issues/44)
* build ci system ([b8fa3eb](https://github.com/Disane87/spoolman-homeassistant/commit/b8fa3eba855c9c6efc3c01a1f08f47b2971abe7e))
* interims commit ([33949b6](https://github.com/Disane87/spoolman-homeassistant/commit/33949b6bc0e5cb2691e3a6349bd10062528c6f7e)), closes [#44](https://github.com/Disane87/spoolman-homeassistant/issues/44) [#44](https://github.com/Disane87/spoolman-homeassistant/issues/44)


## [0.2.2-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.1...v0.2.2-dev.1) (2023-11-02)


### 🛠️ Fixes

* :bug: fixed a bug where location from spoolman is empty ([8ce5abd](https://github.com/Disane87/spoolman-homeassistant/commit/8ce5abd6a90b77ab4f233305ae5475623c042aa0)), closes [#44](https://github.com/Disane87/spoolman-homeassistant/issues/44)
* build ci system ([b8fa3eb](https://github.com/Disane87/spoolman-homeassistant/commit/b8fa3eba855c9c6efc3c01a1f08f47b2971abe7e))
* interims commit ([33949b6](https://github.com/Disane87/spoolman-homeassistant/commit/33949b6bc0e5cb2691e3a6349bd10062528c6f7e)), closes [#44](https://github.com/Disane87/spoolman-homeassistant/issues/44) [#44](https://github.com/Disane87/spoolman-homeassistant/issues/44)

## [0.2.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.0...v0.2.1) (2023-10-07)
### 🛠️ Fixes
* fixed debug logs from info to debug ([f8defbb](https://github.com/Disane87/spoolman-homeassistant/commit/f8defbb56d679573845e98dcd299ea7a19bc376e))

## [0.2.0](https://github.com/Disane87/spoolman-homeassistant/compare/v0.1.3...v0.2.0) (2023-10-05)


### 🛠️ Fixes

* fixed event name + data and added some docs aboiut the usage of the event ([a164d99](https://github.com/Disane87/spoolman-homeassistant/commit/a164d99b5d9ee078f79cc5bab69cf5b7bbb4d51b))
* removed dead code ([9402b15](https://github.com/Disane87/spoolman-homeassistant/commit/9402b15d5fedb7c4bc9248cfec822aa446f5b76e))
* removed dead code + test commit ([bda57bc](https://github.com/Disane87/spoolman-homeassistant/commit/bda57bc08698dc7f6a36f8c5f58fd9728312325a))
* removed openapi.json ([3635ab7](https://github.com/Disane87/spoolman-homeassistant/commit/3635ab7cfe6db5ca68e5b67c62bf520b0493ef96))


### 🚀 Features

* :sparkles: Added thresholds to consume via automations ([af9accc](https://github.com/Disane87/spoolman-homeassistant/commit/af9accc07758f95f33bafa64d091fd0322f39ec2)), closes [#22](https://github.com/Disane87/spoolman-homeassistant/issues/22)
* :sparkles: Spools are now grouped by location ([0be99a0](https://github.com/Disane87/spoolman-homeassistant/commit/0be99a0c72090ff64187efd110f17a8cb773b6c5)), closes [#21](https://github.com/Disane87/spoolman-homeassistant/issues/21)
* Spoolman version in device info closes [#25](https://github.com/Disane87/spoolman-homeassistant/issues/25) ([f3f72eb](https://github.com/Disane87/spoolman-homeassistant/commit/f3f72eb274203f3eff173890a5d49ee09918c724))


### 📔 Docs

* :memo: Fixed typos ([a136657](https://github.com/Disane87/spoolman-homeassistant/commit/a136657d74cb639e3e84f543b22651bd9344e26f))
* :memo: Remove api key references + Updated screenshots to reflect HA icons ([b646fd0](https://github.com/Disane87/spoolman-homeassistant/commit/b646fd0d4463761af1c24a97f6d585828d41a3cf))

## [0.2.0-dev.6](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.0-dev.5...v0.2.0-dev.6) (2023-10-05)


### 🛠️ Fixes

* removed dead code + test commit ([bda57bc](https://github.com/Disane87/spoolman-homeassistant/commit/bda57bc08698dc7f6a36f8c5f58fd9728312325a))

## [0.2.0-dev.5](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.0-dev.4...v0.2.0-dev.5) (2023-10-05)


### 🛠️ Fixes

* removed openapi.json ([3635ab7](https://github.com/Disane87/spoolman-homeassistant/commit/3635ab7cfe6db5ca68e5b67c62bf520b0493ef96))

## [0.2.0-dev.4](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.0-dev.3...v0.2.0-dev.4) (2023-10-05)


### 🛠️ Fixes

* fixed event name + data and added some docs aboiut the usage of the event ([a164d99](https://github.com/Disane87/spoolman-homeassistant/commit/a164d99b5d9ee078f79cc5bab69cf5b7bbb4d51b))

## [0.2.0-dev.3](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.0-dev.2...v0.2.0-dev.3) (2023-10-04)


### 🚀 Features

* Spoolman version in device info closes [#25](https://github.com/Disane87/spoolman-homeassistant/issues/25) ([f3f72eb](https://github.com/Disane87/spoolman-homeassistant/commit/f3f72eb274203f3eff173890a5d49ee09918c724))

## [0.2.0-dev.2](https://github.com/Disane87/spoolman-homeassistant/compare/v0.2.0-dev.1...v0.2.0-dev.2) (2023-10-04)


### 🚀 Features

* :sparkles: Added thresholds to consume via automations ([af9accc](https://github.com/Disane87/spoolman-homeassistant/commit/af9accc07758f95f33bafa64d091fd0322f39ec2)), closes [#22](https://github.com/Disane87/spoolman-homeassistant/issues/22)

## [0.2.0-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.1.4-dev.1...v0.2.0-dev.1) (2023-10-04)


### 🚀 Features

* :sparkles: Spools are now grouped by location ([0be99a0](https://github.com/Disane87/spoolman-homeassistant/commit/0be99a0c72090ff64187efd110f17a8cb773b6c5)), closes [#21](https://github.com/Disane87/spoolman-homeassistant/issues/21)

## [0.1.4-dev.1](https://github.com/Disane87/spoolman-homeassistant/compare/v0.1.3...v0.1.4-dev.1) (2023-10-04)


### 🛠️ Fixes

* removed dead code ([9402b15](https://github.com/Disane87/spoolman-homeassistant/commit/9402b15d5fedb7c4bc9248cfec822aa446f5b76e))


### 📔 Docs

* :memo: Fixed typos ([a136657](https://github.com/Disane87/spoolman-homeassistant/commit/a136657d74cb639e3e84f543b22651bd9344e26f))
* :memo: Remove api key references + Updated screenshots to reflect HA icons ([b646fd0](https://github.com/Disane87/spoolman-homeassistant/commit/b646fd0d4463761af1c24a97f6d585828d41a3cf))
