# Analog Subway Clock

An analog clock whose hands show the time until the next downtown 1 train arrives at 125th Street (NYC MTA). Runs on a Raspberry Pi Zero 2 W.

## How It Works

The software polls the MTA's public GTFS-Realtime feed every 30 seconds, parses the protobuf response, and extracts arrival predictions for the southbound 1 train at 125th St (GTFS stop `116S`). The number of minutes until the next arrival is then mapped to a position on the clock face, driven by a stepper motor.

This is a Python translation of the [SubwayTimeService](../SubwayTimeService) Go project, stripped of AWS infrastructure (Lambda, DynamoDB, API Gateway) and adapted to run locally on the Pi.

## Project Structure

```
analog_clock/
  config.py             # Station, route, feed URL, polling interval
  mta_feed.py           # Fetches + parses GTFS-Realtime protobuf from MTA
  subway_times.py       # Caching layer, computes minutes-to-arrival
  clock_controller.py   # Stub for stepper motor / hall sensor control
  main.py               # Entry point — poll loop
  requirements.txt      # Python dependencies
```

## Setup (Local / Development)

```bash
# Install uv if you don't have it:
curl -LsSf https://astral.sh/uv/install.sh | sh

uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
uv run main.py
```

No API key is needed — the MTA GTFS-Realtime endpoint is public.

## Deploying to Raspberry Pi Zero 2 W

### 1. OS Setup

Flash **Raspberry Pi OS Lite (64-bit)** onto a microSD card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/). In the imager's settings:
- Enable SSH
- Set your Wi-Fi credentials
- Set a hostname (e.g., `subwayclock.local`)

### 2. SSH In and Install Dependencies

```bash
ssh pi@subwayclock.local

# Update system
sudo apt update && sudo apt upgrade -y

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone or copy your code to the Pi
# Option A: git clone
# Option B: scp -r analog_clock/ pi@subwayclock.local:~/analog_clock/

cd ~/analog_clock
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Test It

```bash
uv run main.py
```

You should see log output like:
```
2026-04-05 12:00:00 [__main__] INFO: Analog subway clock starting
2026-04-05 12:00:01 [mta_feed] INFO: 1 train at 116S arriving Sat Apr 05 12:04:30 EDT (4.5 min)
2026-04-05 12:00:01 [__main__] INFO: Next 1 train downtown in 4.5 min | upcoming: ['4.5', '12.3', '20.1']
```

### 4. Run on Boot (systemd)

Create a service file:

```bash
sudo nano /etc/systemd/system/subwayclock.service
```

```ini
[Unit]
Description=Analog Subway Clock
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/analog_clock
ExecStart=/home/pi/analog_clock/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable subwayclock
sudo systemctl start subwayclock

# Check logs:
journalctl -u subwayclock -f
```

## Next Steps: Hardware Integration

### Stepper Motors

You'll need a stepper motor to drive the clock hand(s). Common choices for small clocks:

- **28BYJ-48** with ULN2003 driver board — cheap, widely available, fine for a clock hand. ~$3 on Amazon. 5V, works directly with Pi GPIO.
- **NEMA 17** with A4988 or DRV8825 driver — more torque/precision, but overkill for a single clock hand.

The 28BYJ-48 is the typical choice for clock projects. It has 2048 steps per revolution (in half-step mode), which gives you ~0.18 degrees per step — more than enough precision.

**Wiring (28BYJ-48 + ULN2003):**
- ULN2003 IN1–IN4 connect to 4 GPIO pins on the Pi
- ULN2003 power: 5V and GND from the Pi's 5V pin

**Python library:** Use `RPi.GPIO` (pre-installed on Pi OS) or the `gpiozero` library. Add to `requirements.txt` when on the Pi:
```
RPi.GPIO>=0.7.0
```

### Hall Effect Sensor (Home Position Detection)

A hall effect sensor detects a small magnet attached to the clock hand, so the software knows the hand's absolute position on startup (the "home" position).

- **A3144** (digital, latching) or **SS49E** (analog) — either works. The A3144 is simplest: it outputs HIGH/LOW based on magnet presence.
- Attach a small magnet to the clock hand shaft or hand itself.
- Mount the sensor at the 12 o'clock (0 minute) position.

**Wiring (A3144):**
- VCC to 3.3V
- GND to GND
- Signal to a GPIO pin (with a 10k pull-up resistor)

**Homing procedure on startup:**
1. Slowly step the motor forward
2. Read the hall sensor each step
3. When the sensor triggers, you've found 0 — record this as the reference position
4. Now you can move to any angle by counting steps from home

### Implementation Plan

1. Get the software running on the Pi and confirming train times (current state)
2. Wire up the stepper motor + driver, test basic stepping with a simple script
3. Wire up the hall sensor, implement the homing routine
4. Fill in `clock_controller.py` with real GPIO code to map minutes to motor position
5. Build/mount the clock face and hand
6. Set up systemd for auto-start on boot

### Useful Resources

- `gpiozero` docs: https://gpiozero.readthedocs.io/
- 28BYJ-48 Pi tutorial: search "28BYJ-48 raspberry pi python"
- MTA GTFS-Realtime reference: https://api.mta.info/
- Raspberry Pi GPIO pinout: https://pinout.xyz/
