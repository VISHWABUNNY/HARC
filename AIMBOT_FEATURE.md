# Manual + Aim-Bot Feature

## Overview

Added a new system mode: **"Manual + Aim-Bot"** that combines manual joystick control with AI-powered aim-bot assistance.

## Feature Description

### Manual + Aim-Bot Mode

- **User Control**: Joystick input is primary - user has full manual control
- **Aim-Bot Assistance**: AI automatically helps guide the cannon toward detected targets
- **Blended Input**: Joystick movement is blended with aim-bot suggestions
- **Smart Assistance**: Assistance strength increases as you get closer to targets

## How It Works

1. **Target Detection**: System continuously detects humans from camera feed
2. **Target Selection**: AI selects best target (highest confidence, closest, center of frame)
3. **Assistance Calculation**: Calculates direction from current cannon position to target
4. **Input Blending**: Blends joystick input with aim-bot direction:
   - Formula: `(1 - strength) × joystick + strength × aim_bot`
   - Closer to target = stronger assistance
   - User always has control (joystick input is never overridden)

## Technical Implementation

### Backend Services

1. **AimBotAssistanceService** (`app/services/aimbot_assistance_service.py`)
   - Manages aim-bot assistance state
   - Calculates target priority
   - Blends joystick input with aim-bot suggestions
   - Configurable assistance strength (0.0 to 1.0)

2. **JoystickMotorBridge** (updated)
   - Now supports mode switching
   - Receives detected humans from tracking API
   - Applies aim-bot assistance when in "Manual + Aim-Bot" mode

3. **System Service** (updated)
   - Manages aim-bot assistance service
   - Handles mode switching

### API Endpoints

New endpoints for aim-bot assistance:

- `POST /api/system/aimbot-assistance/start` - Start aim-bot assistance
- `POST /api/system/aimbot-assistance/stop` - Stop aim-bot assistance
- `GET /api/system/aimbot-assistance/status` - Get aim-bot status

### Frontend Updates

1. **Mode Selector** - Added "Manual + Aim-Bot" option
2. **Live Feed Card** - Auto-analyzes in aim-bot mode for continuous assistance
3. **Weapon Control Card** - Shows joystick in aim-bot mode
4. **API Client** - Added aim-bot assistance functions

## Configuration

### Assistance Strength

Default: `0.5` (50% assistance)

Can be adjusted in `AimBotAssistanceService`:
```python
self.assistance_strength = 0.5  # 0.0 = no help, 1.0 = maximum help
```

### Target Selection Criteria

Aim-bot selects targets based on:
1. **Confidence** (50% weight) - Higher confidence = better target
2. **Distance** (30% weight) - Closer targets = higher priority
3. **Center Position** (20% weight) - Targets near center of frame = easier to aim

### Assistance Range

- **Very Close** (< 10°): Full assistance strength
- **Medium** (10-20°): 70% assistance strength
- **Far** (> 20°): 30% assistance strength

## Usage

1. **Select Mode**: Choose "Manual + Aim-Bot" from mode selector
2. **Enable Camera**: Ensure camera feed is active
3. **Use Joystick**: Move joystick normally - aim-bot will assist
4. **Feel the Assistance**: As you get closer to targets, assistance increases

## Mode Comparison

| Mode | User Control | AI Control | Use Case |
|------|-------------|------------|----------|
| **Manual** | Full | None | Complete manual control |
| **Manual + Aim-Bot** | Primary | Assistance | Manual control with targeting help |
| **Full Auto** | None | Full | Fully automatic targeting |

## Benefits

✅ **Enhanced Accuracy**: AI helps guide to targets  
✅ **User Control**: User always has final say  
✅ **Adaptive**: Assistance strength adapts to distance  
✅ **Non-Intrusive**: Doesn't override user input  
✅ **Real-time**: Continuous assistance as targets move  

## Future Enhancements

Possible improvements:
- Adjustable assistance strength via UI
- Different assistance profiles (light/medium/strong)
- Target prediction (lead targets based on movement)
- Haptic feedback for target lock
- Visual indicators showing aim-bot assistance direction

---

**Version**: 1.1.0  
**Added**: December 2024

