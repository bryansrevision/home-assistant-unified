# 🔧 Android Integration Maintenance Guide

## Overview
This guide provides procedures for maintaining, updating, and optimizing your Android integration with your home automation infrastructure.

---

## Table of Contents
- [Regular Maintenance Tasks](#regular-maintenance-tasks)
- [Update Procedures](#update-procedures)
- [Performance Optimization](#performance-optimization)
- [Backup Procedures](#backup-procedures)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [Long-Term Optimization](#long-term-optimization)

---

## Regular Maintenance Tasks

### Daily Tasks (Automated)

These should run automatically:

```yaml
# Automation for daily health check
automation:
  - alias: "Daily Android Integration Health Check"
    trigger:
      - platform: time
        at: "23:00:00"
    action:
      - service: notify.mobile_app_primary_android
        data:
          message: |
            Daily Summary:
            Battery: {{ states('sensor.mobile_app_primary_android_battery_level') }}%
            Location updates: {{ states('sensor.location_update_count') }}
            Automations triggered: {{ states('sensor.automation_count_today') }}
          title: "Daily Health Check"
```

**No manual action required** unless health check reports issues.

---

### Weekly Tasks (5-10 minutes)

#### 1. Review Automation Performance

**Check**:
```
Home Assistant > Configuration > Automations > [Each Android automation]
- Click on automation
- Review "Last Triggered"
- Check execution times
- Look for errors in traces
```

**What to look for**:
- ❌ Automations that never trigger (may need adjustment)
- ❌ Automations triggering too frequently (add delays)
- ❌ Automations with errors in execution

**Action**:
- Adjust triggers/conditions as needed
- Disable unused automations
- Document any changes

#### 2. Check Battery Usage

**Steps**:
```
1. Android Settings > Battery > Battery usage
2. Find "Home Assistant" app
3. Check percentage of battery used
4. Compare to previous week
```

**Acceptable Range**:
- ✅ < 3% per day: Excellent
- ⚠️ 3-5% per day: Normal
- ❌ > 5% per day: Needs optimization (see optimization section)

**If high**:
- Disable unnecessary sensors
- Increase update intervals
- Reduce widget refresh frequency

#### 3. Verify Notification Delivery

**Test**:
```yaml
# Send test notification from HA
service: notify.mobile_app_primary_android
data:
  message: "Weekly test - {{ now().strftime('%Y-%m-%d %H:%M') }}"
  title: "Test Notification"
```

**Check**:
- Notification received within 10 seconds?
- Actionable buttons work?
- Images display correctly?

**If issues**: See [Troubleshooting Guide](./docs/troubleshooting/ANDROID_TROUBLESHOOTING.md)

#### 4. Review Location Tracking

**Check**:
```
Home Assistant > Map
- Verify your location is current
- Check for GPS drift
- Verify zone transitions are accurate
```

**Home Assistant > History**:
```
- Select device_tracker.mobile_app_primary_android
- Review last 7 days
- Look for:
  ❌ Frequent zone changes (false triggers)
  ❌ Long delays in updates
  ❌ "Unavailable" states
```

---

### Monthly Tasks (15-30 minutes)

#### 1. Update All Apps

**Android System**:
```
Settings > System > System update
Check for updates
Install if available
```

**Home Assistant Companion App**:
```
Play Store > My apps & games > Updates
Update Home Assistant app
Review changelog for new features
```

**Other Apps**:
```
Play Store > Update all
Especially: Tailscale, Bitwarden, MQTT clients
```

#### 2. Review and Rotate Credentials

**Long-Lived Access Token**:
```
Home Assistant > Profile > Long-Lived Access Tokens
- Check creation date
- If > 6 months old, create new token
- Update in HA Companion app
- Delete old token
```

**Bitwarden**:
```
- Review password strength
- Change any weak passwords
- Enable 2FA if not already enabled
```

#### 3. Clean Up Automations

**Review all Android automations**:
```
Home Assistant > Configuration > Automations
Filter by "android"

For each automation:
- Is it still needed? (Disable if not)
- Is it triggering correctly? (Check traces)
- Could it be optimized? (Fewer conditions, better logic)
```

**Clean up disabled automations**:
- Delete automations disabled for > 3 months
- Document reason for deletion

#### 4. Database Cleanup

**Check Database Size**:
```
Home Assistant > System > Storage
- Check "Database" size
- If > 1GB, consider cleanup
```

**Exclude Unnecessary Data**:
```yaml
# configuration.yaml
recorder:
  purge_keep_days: 30  # Reduce if database too large
  exclude:
    entities:
      - sensor.mobile_app_primary_android_light_sensor
      - sensor.mobile_app_primary_android_pressure_sensor
```

**Manual Purge** (if needed):
```
Developer Tools > Services
Service: recorder.purge
Data:
  keep_days: 7  # Purge older than 7 days
  repack: true   # Reclaim space
```

#### 5. Backup Verification

**Test Backup Restoration**:
```
1. Download latest Home Assistant backup
2. Verify backup is not corrupted
3. Test restore on test system (if available)
4. Document any issues
```

**Verify Android App Export**:
```
HA Companion App > App Configuration
- Review sensor configurations
- Screenshot widget settings
- Save to Bitwarden secure note
```

---

### Quarterly Tasks (1-2 hours)

#### 1. Full System Update

**Home Assistant Core**:
```
1. Review release notes
2. Check breaking changes
3. Backup before update
4. Update Home Assistant
5. Test all Android integrations
6. Check logs for errors
```

**Proxmox VE**:
```
1. Update all VMs
2. Update all LXC containers
3. Update Proxmox host
4. Test VM controls from Android
```

**Router/Firewall**:
```
1. Update firmware
2. Review firewall rules
3. Check VPN settings
4. Test remote access
```

#### 2. Security Audit

**Review Access**:
```
Home Assistant > Configuration > Users
- Review all users
- Disable unused accounts
- Check permissions
- Review recent logins
```

**Check Logs**:
```
Configuration > Logs
Filter by "error" and "warning"
Look for:
- Failed login attempts
- Unauthorized access attempts
- Certificate errors
```

**Update Security**:
- Change important passwords
- Rotate API tokens
- Review 2FA settings
- Check Tailscale ACLs

#### 3. Performance Review

**Check Response Times**:
```
Test from Android:
- Widget updates: < 2 seconds
- Dashboard load: < 3 seconds
- Automation trigger: < 1 second
- Notification delivery: < 10 seconds
```

**If slow**:
- Check network speed
- Review database size
- Optimize automations
- Reduce enabled sensors

#### 4. Automation Optimization

**Review automation performance**:
```
Configuration > Automations > [Automation] > Traces
- Check execution times
- Identify slow automations
- Optimize where possible
```

**Common optimizations**:
```yaml
# Use parallel actions when possible
action:
  - parallel:
      - service: light.turn_off
      - service: lock.lock
      - service: climate.set_preset_mode

# Use choose instead of nested if/then
action:
  - choose:
      - conditions: [...]
        sequence: [...]
      - conditions: [...]
        sequence: [...]
```

---

## Update Procedures

### Home Assistant Companion App Update

**Before Update**:
1. ✅ Export app settings (App Configuration > ...)
2. ✅ Screenshot widget configurations
3. ✅ Note automation that use app events

**Update Process**:
```
Play Store > Home Assistant > Update
Wait for update to complete
Open app
Verify connection to Home Assistant
```

**After Update**:
1. ✅ Test notification delivery
2. ✅ Verify location updates
3. ✅ Check sensors are still enabled
4. ✅ Test widgets and quick settings tiles
5. ✅ Review changelog for new features

**If Issues**:
- Clear app cache
- Restart phone
- Reconnect to Home Assistant
- See troubleshooting guide

---

### Home Assistant Core Update

**Pre-Update Checklist**:
```
1. ✅ Full backup of Home Assistant
2. ✅ Read release notes for breaking changes
3. ✅ Check Android integration compatibility
4. ✅ Schedule during low-usage time
5. ✅ Have rollback plan ready
```

**Update Process**:
```
Home Assistant > Configuration > Updates
- Click "Update" on Home Assistant Core
- Wait for update to complete (5-15 minutes)
- Home Assistant will restart
```

**Post-Update Checklist**:
```
1. ✅ Verify Home Assistant started successfully
2. ✅ Check Android app reconnects
3. ✅ Test notification delivery
4. ✅ Verify automations still work
5. ✅ Check for errors in logs
6. ✅ Test critical functions (locks, security, etc.)
```

**Breaking Changes**:
```
If release has breaking changes for mobile_app:
1. Review migration guide in release notes
2. Update configurations as needed
3. Test thoroughly before relying on changes
```

**Rollback** (if update fails):
```
1. Restore from backup taken before update
2. Report issue to Home Assistant GitHub
3. Wait for hotfix or skip version
```

---

### Android OS Update

**Pre-Update**:
```
1. ✅ Ensure phone is charged (> 50%)
2. ✅ Connect to WiFi
3. ✅ Backup phone (Google backup)
4. ✅ Export HA app settings
5. ✅ Note all installed automation apps
```

**Update Process**:
```
Settings > System > System update
Download and install
Phone will restart (10-30 minutes)
```

**Post-Update**:
```
1. ✅ Verify Home Assistant app works
2. ✅ Check all permissions still granted
3. ✅ Verify battery optimization still disabled
4. ✅ Test location services
5. ✅ Test notifications
6. ✅ Verify Tailscale VPN works
7. ✅ Check widgets are still configured
8. ✅ Test automations
```

**Common Issues After Android Update**:
- Permissions reset → Re-grant all permissions
- Battery optimization re-enabled → Disable again
- Widgets broken → Remove and re-add
- VPN disconnected → Reconnect Tailscale

---

## Performance Optimization

### Reducing Battery Drain

**Step 1: Identify Battery Hogs**:
```
Settings > Battery > Battery usage
- Identify high-usage apps
- Focus on Home Assistant if > 5%/day
```

**Step 2: Optimize Sensors**:
```
HA Companion App > App Configuration > Sensors

Disable unnecessary sensors:
❌ Light sensor (if not used)
❌ Pressure sensor (if not used)
❌ Proximity sensor (if not used)
❌ Step counter (if not used)

Reduce update frequency:
✓ Battery: 15 minutes → 30 minutes
✓ Location: 60 seconds → 120 seconds
✓ Network: 5 minutes → 15 minutes
```

**Step 3: Optimize Widgets**:
```
- Remove dashboard widgets (refresh frequently)
- Use button widgets instead
- Increase refresh intervals
- Limit to 2-3 widgets maximum
```

**Step 4: Optimize Automations**:
```yaml
# Batch notifications instead of sending each one
automation:
  - alias: "Batched Daily Summary"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      # Send one notification with all info
      # Instead of multiple throughout the day
```

### Improving Responsiveness

**Optimize Home Assistant**:
```yaml
# Enable recorder optimizations
recorder:
  commit_interval: 5  # More frequent commits
  exclude:
    domains:
      - automation
      - script
    entity_globs:
      - sensor.mobile_app_*_light_sensor
```

**Optimize Network**:
```
- Use 5GHz WiFi band (faster)
- Place WiFi access points strategically
- Minimize interference
- Use WiFi 6 if available
```

**Optimize Android**:
```
- Close unused apps
- Clear cache regularly
- Restart phone weekly
- Keep storage > 10% free
```

---

## Backup Procedures

### Home Assistant Configuration Backup

**Automated Backups**:
```yaml
# Create automation for daily backups
automation:
  - alias: "Daily HA Backup"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: backup.create
```

**Manual Backup**:
```
Home Assistant > Configuration > Backups
- Click "Create Backup"
- Include all add-ons and configurations
- Download to computer
- Upload to cloud storage
```

**What to Backup**:
- ✅ All configuration files
- ✅ Automations
- ✅ Scripts
- ✅ Secrets
- ✅ Custom integrations
- ✅ Database (optional, can be large)

### Android App Configuration Backup

**Export Settings**:
```
HA Companion App > App Configuration
- Screenshot all sensor settings
- Document widget configurations
- Note quick settings tile setups
- Save to Bitwarden secure note
```

**Document Configuration**:
```markdown
# Android Integration Config - [Date]

## Sensors Enabled:
- Location: On, 60s interval
- Battery: On, 15m interval
- Activity: On
- [... etc]

## Widgets:
1. Home screen 1: Essential Controls (2x2)
2. Home screen 1: Security (2x2)
[... etc]

## Automations:
- Welcome Home: Enabled
- Away Mode: Enabled
[... etc]
```

### Cloud Backup Strategy

**Three-Tier Backup**:
```
Tier 1 (Local): 
- Proxmox VE backups
- NAS storage
- Refresh: Daily

Tier 2 (Cloud):
- Google Drive
- Dropbox
- Refresh: Weekly

Tier 3 (Cold Storage):
- External hard drive (off-site)
- Refresh: Monthly
```

---

## Long-Term Optimization

### Every 6 Months

**1. Complete System Review**:
- Audit all automations
- Remove unused entities
- Optimize database
- Review integrations

**2. Technology Updates**:
- Check for new Android features
- Review HA Companion app updates
- Explore new integrations
- Update documentation

**3. User Experience**:
- Survey family members
- Identify pain points
- Optimize workflows
- Update automations

### Annual Tasks

**1. Major Infrastructure Updates**:
- Upgrade Home Assistant (major version)
- Update Proxmox VE
- Replace aging hardware
- Review architecture

**2. Complete Reconfiguration**:
- Clean slate review
- Remove technical debt
- Implement best practices
- Update security measures

**3. Disaster Recovery Test**:
- Full system restore from backup
- Test all failover procedures
- Verify remote access
- Document lessons learned

---

## Maintenance Schedule Template

### Quick Reference

```
Daily (Automated):
  ✓ Health check notification
  ✓ Backup to local storage

Weekly (5 minutes):
  ☐ Review automation performance
  ☐ Check battery usage
  ☐ Test notifications
  ☐ Verify location tracking

Monthly (30 minutes):
  ☐ Update all apps
  ☐ Review and rotate credentials
  ☐ Clean up automations
  ☐ Database cleanup
  ☐ Backup verification

Quarterly (2 hours):
  ☐ Full system update
  ☐ Security audit
  ☐ Performance review
  ☐ Automation optimization

Semi-Annually (4 hours):
  ☐ Complete system review
  ☐ Technology updates
  ☐ User experience improvements

Annually (8 hours):
  ☐ Major infrastructure updates
  ☐ Complete reconfiguration
  ☐ Disaster recovery test
```

---

## Maintenance Log Template

Keep a log of all maintenance activities:

```markdown
# Maintenance Log

## [Date]

### Tasks Completed:
- [ ] Weekly battery check: 3.2%/day ✓
- [ ] Automation review: All functioning ✓
- [ ] Notification test: Successful ✓

### Issues Found:
- None

### Actions Taken:
- Disabled light sensor (not used)
- Increased location update interval to 120s

### Next Steps:
- Monitor battery usage next week
- Consider adding new automation for morning routine

---

## [Previous Date]
...
```

---

## Support Resources

### When You Need Help

**Official Documentation**:
- Home Assistant: https://www.home-assistant.io/docs/
- HA Companion App: https://companion.home-assistant.io/
- Tailscale: https://tailscale.com/kb/

**Community Support**:
- Home Assistant Community Forum
- r/homeassistant on Reddit
- Home Assistant Discord

**Professional Help**:
- Home Assistant Cloud Support (Nabu Casa subscribers)
- Local home automation consultants
- Smart home installers

---

## Best Practices

### Do's ✅
- ✅ Keep regular backups
- ✅ Test before major changes
- ✅ Document all configurations
- ✅ Monitor battery usage
- ✅ Review logs regularly
- ✅ Update apps promptly
- ✅ Optimize periodically

### Don'ts ❌
- ❌ Skip backups before updates
- ❌ Ignore error messages
- ❌ Leave battery optimization enabled
- ❌ Delay security updates
- ❌ Overcomplicate automations
- ❌ Forget to test changes
- ❌ Neglect documentation

---

**Remember**: Regular maintenance prevents major issues. Spend 30 minutes monthly to save hours of troubleshooting! 🔧
