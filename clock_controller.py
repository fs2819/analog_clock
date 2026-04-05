"""Clock controller stub — interface between subway times and the physical clock.

This module is a placeholder for the stepper motor / hall effect sensor control
that will run on the Raspberry Pi. The actual GPIO implementation will depend on
your hardware wiring and motor driver setup.

For now, it logs what the clock hands should show.
"""

import logging

logger = logging.getLogger(__name__)

# Maximum minutes the clock face represents (one full revolution of the minute hand).
# For example, if the clock face goes from 0–30 minutes, set this to 30.
CLOCK_MAX_MINUTES = 30


def update_clock_hands(train_minutes: list[float | None]) -> None:
    """Set all three clock hands to display the next 3 train arrival times.

    Args:
        train_minutes: List of 3 values — minutes until each of the 3 closest
            trains. None entries mean no train data for that hand.
    """
    for i, minutes in enumerate(train_minutes):
        hand = i + 1
        if minutes is None:
            logger.warning("Hand %d: no train data — idle", hand)
            # TODO: move hand to a "no data" position
            continue

        if minutes > CLOCK_MAX_MINUTES:
            logger.info(
                "Hand %d: %.1f min (beyond clock range of %d min)",
                hand,
                minutes,
                CLOCK_MAX_MINUTES,
            )
            # TODO: peg hand at max
            continue

        logger.info("Hand %d: setting to %.1f minutes", hand, minutes)

        # --- Stepper motor logic goes here ---
        # Convert minutes to a target angle:
        #   angle = (minutes / CLOCK_MAX_MINUTES) * 360
        #
        # Then command stepper motor #hand to move to that angle.
        # Use the hall effect sensor to determine current hand position
        # so you know how far to step.
        #
        # Example (pseudocode):
        #   target_angle = (minutes / CLOCK_MAX_MINUTES) * 360
        #   current_angle = read_hall_sensor_position(hand)
        #   delta = target_angle - current_angle
        #   step_motor(hand, delta)
