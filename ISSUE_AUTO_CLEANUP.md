# 🧹 Auto-cleanup of old location devices in v2.0+

## 📋 Summary

Version 2.0+ introduces automatic cleanup of old location devices from previous versions.

## 🔍 Background

In versions prior to 2.0, this integration created separate devices for locations. With the new architecture:
- Locations now act as organizational "hubs" (parent devices)
- Spools are child devices under their respective location hubs
- Old standalone location devices became empty/orphaned after the update

## ✨ What's Implemented

The integration now includes automatic migration logic that:
- ✅ Detects old location devices on startup (identified by `location_X` identifiers)
- ✅ Automatically removes them from the device registry
- ✅ Logs the cleanup process for transparency
- ✅ Leaves spool devices completely untouched

## 🎯 User Experience

Users upgrading from older versions will notice:
1. After updating and restarting Home Assistant
2. Old location devices are automatically removed
3. Log message confirms: "Migration complete: Removed X old location device(s)"
4. No manual intervention needed! 🎉

## 📝 Implementation Details

**File**: `custom_components/spoolman/__init__.py`
**Function**: `_async_remove_old_location_devices()`
**Trigger**: Runs during `async_setup_entry`

The function:
- Gets device registry entries for the integration
- Checks device identifiers for `location_` prefix
- Removes matching devices
- Logs the cleanup operation

## 📚 Documentation

Updated README.md with:
- Clear explanation of the auto-cleanup process
- Migration instructions for users
- Technical details about what's changed

## 🔗 Related

This resolves the issue where users would see empty location devices after upgrading to v2.0+.

## ✅ Testing Checklist

- [ ] Fresh install (should not trigger cleanup)
- [ ] Upgrade from v1.x with location devices (should clean up automatically)
- [ ] Multiple restarts (cleanup should be idempotent)
- [ ] Log messages appear correctly

---

**Labels**: `enhancement`, `documentation`, `migration`
